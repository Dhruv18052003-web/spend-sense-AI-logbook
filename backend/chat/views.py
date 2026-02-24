import logging
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Sum
from records.models import Records
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Wallet

from chat.add_money_extractor import add_money_extractor
from chat.intent_classifier import classify_intent
from chat.models import ChatLogs
from chat.query_extractor import extract_query
from chat.query_response_generator import generate_query_response
from chat.response_generator import generate_log_expense_response
from chat.semantic_resolver import resolve_semantic
from chat.services.expense_pipeline import process_expense_message
from chat.chitchat_response import generate_chitchat_response
from chat.gretting_response import generate_greeting_response
from chat.query_scope_agent import classify_query_scope
from chat.semantic_expansion_agent import expand_semantic_scope

logger = logging.getLogger("chat")


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        limit_param = request.query_params.get("limit", "50")
        try:
            limit = int(limit_param)
        except (TypeError, ValueError):
            limit = 50

        limit = max(1, min(limit, 100))

        logs = list(
            ChatLogs.objects.filter(user=user)
            .order_by("-created_at")[:limit]
        )
        logs.reverse()

        messages = []
        for log in logs:
            messages.append({"role": "user", "content": log.user_prompt})
            messages.append({"role": "assistant", "content": log.ai_response})

        wallet, _ = Wallet.objects.get_or_create(user=user)
        currency_code = self._get_user_currency(user)

        return Response(
            {
                "messages": messages,
                "remaining_balance": str(wallet.balance),
                "currency": currency_code,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        user = request.user
        user_message = request.data.get("message")

        if not user_message:
            return Response(
                {"error": "message is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        intent_result = classify_intent(user_message)
        intent = intent_result.get("intent")
        logger.info(
            "intent_classified user=%s intent=%s message=%s",
            user.username,
            intent,
            user_message,
        )

        if intent == "log_expense":
            return self.handle_log_expense(user, user_message)
        if intent == "add_money":
            return self.handle_add_money(user, user_message)
        if intent == "query_analysis":
            return self.handle_query(user, user_message)
        elif intent == "greetings": 
            return self.handle_greeting(user, user_message) 
        elif intent == "chitchat": 
            return self.handle_chitchat(user, user_message) 

        return Response(
            {"reply": "Sorry, I could not understand that."},
            status=status.HTTP_200_OK,
        )

    def _get_user_currency(self, user):
        profile = getattr(user, "profile", None)
        if profile and profile.currency:
            return profile.currency
        return "INR"

    def handle_log_expense(self, user, user_message):
        result = process_expense_message(user, user_message)

        missing_fields = []
        if not result.get("raw_label"):
            missing_fields.append("item")
        if not result.get("amount"):
            missing_fields.append("amount")

        if missing_fields:
            event_data = {
                "event": "log_expense_incomplete",
                "missing_fields": missing_fields,
            }
            reply_text = generate_log_expense_response(user_message, event_data)
            ChatLogs.objects.create(
                user=user,
                user_prompt=user_message,
                ai_response=reply_text,
            )
            return Response({"reply": reply_text}, status=status.HTTP_200_OK)

        with transaction.atomic():
            Records.objects.create(
                user=user,
                raw_label=result["raw_label"],
                semantic_concept=result["semantic_concept"],
                amount=result["amount"],
                spent_at=result["spent_at"],
            )

            wallet, _ = Wallet.objects.get_or_create(user=user)
            expense_amount = Decimal(str(result["amount"]))
            wallet.balance -= expense_amount
            wallet.save()

            currency_code = self._get_user_currency(user)

            event_data = {
                "event": "log_expense",
                "item": result["raw_label"],
                "amount": result["amount"],
                "currency": currency_code,
                "spent_at": result["spent_at"].isoformat(),
            }

            reply_text = generate_log_expense_response(user_message, event_data)

            ChatLogs.objects.create(
                user=user,
                user_prompt=user_message,
                ai_response=reply_text,
            )

        return Response(
            {
                "reply": reply_text,
                "remaining_balance": str(wallet.balance),
                "currency": currency_code,
            },
            status=status.HTTP_200_OK,
        )

    def handle_add_money(self, user, user_message):
        extracted = add_money_extractor(user_message)
        amount = extracted.get("amount")

        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, TypeError):
            amount = None

        if amount is None or amount <= 0:
            event_data = {
                "event": "add_money_incomplete",
                "missing_fields": ["amount"],
            }
            reply_text = generate_log_expense_response(user_message, event_data)

            ChatLogs.objects.create(
                user=user,
                user_prompt=user_message,
                ai_response=reply_text,
            )

            return Response({"reply": reply_text}, status=status.HTTP_200_OK)

        with transaction.atomic():
            wallet, _ = Wallet.objects.get_or_create(user=user)
            wallet.balance += Decimal(str(amount))
            wallet.save()
            currency_code = self._get_user_currency(user)

            event_data = {
                "event": "add_money",
                "amount": str(amount),
                "currency": currency_code,
                "remaining_balance": str(wallet.balance),
            }

            reply_text = generate_log_expense_response(user_message, event_data)

            ChatLogs.objects.create(
                user=user,
                user_prompt=user_message,
                ai_response=reply_text,
            )

        return Response(
            {
                "reply": reply_text,
                "remaining_balance": str(wallet.balance),
                "currency": currency_code,
            },
            status=status.HTTP_200_OK,
        )

    def resolve_time_range(self, time_range: dict):
        today = date.today()

        if not time_range:
            return None, None

        range_type = time_range.get("type")
        value = time_range.get("value")

        if range_type == "today":
            return today, today

        if range_type == "yesterday":
            y = today - timedelta(days=1)
            return y, y

        if range_type == "this_month":
            start = today.replace(day=1)
            return start, today

        if range_type == "last_month":
            first_this_month = today.replace(day=1)
            last_month_end = first_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return last_month_start, last_month_end

        if range_type == "last_n_days" and value:
            start = today - timedelta(days=value)
            return start, today

        return None, None
    
    def apply_semantic_filter(qs, user, user_message, semantic):
        resolved_concept = resolve_semantic(user, semantic)
        scope = classify_query_scope(user_message, semantic)

        if scope == "specific":
            return qs.filter(semantic_concept=resolved_concept)

        expanded_ids = expand_semantic_scope(resolved_concept.semantic_id)

        return qs.filter(
            semantic_concept__semantic_id__in=expanded_ids
        )


    def handle_query(self, user, user_message):

        print("[QueryFlow] step=1 start user_message:", user_message)

        # 1) Extract structured query info using LLM
        query = extract_query(user_message)
        print("[QueryFlow] extracted_query:", query)

        query_type = query.get("query_type")
        metric = query.get("metric")
        semantic = query.get("semantic_concept")
        time_range = query.get("time_range")

        print(
            "[QueryFlow] step=2 extracted_fields:",
            {
                "query_type": query_type,
                "metric": metric,
                "semantic": semantic,
                "time_range": time_range,
            },
        )

        # 2) Validate minimum required fields
        if not query_type or not metric or not time_range:
            print("[QueryFlow] validation_failed -> query_unsupported")
            reply_text = generate_query_response(
                user_message,
                {"event": "query_unsupported"}
            )

            ChatLogs.objects.create(
                user=user,
                user_prompt=user_message,
                ai_response=reply_text,
            )

            return Response({"reply": reply_text})

        # 3) Resolve time range
        start_date, end_date = self.resolve_time_range(time_range)
        print("[QueryFlow] step=3 time_range_resolved:", start_date, end_date)

        # 4) Base queryset (user + date filter)
        qs = Records.objects.filter(user=user)
        print("[QueryFlow] step=4 base_count:", qs.count())

        if start_date and end_date:
            qs = qs.filter(spent_at__range=(start_date, end_date))
            print("[QueryFlow] step=4 after_date_filter_count:", qs.count())

        # 5) Apply semantic filtering if present
        if semantic:
            try:
                resolved_concept = resolve_semantic(user, semantic)
                print("[QueryFlow] step=5 resolved_semantic:", resolved_concept.semantic_id)

                scope = classify_query_scope(user_message, resolved_concept.semantic_id)
                print("[QueryFlow] step=5 scope:", scope)

                if scope == "specific":
                    qs = qs.filter(semantic_concept=resolved_concept)
                    print("[QueryFlow] step=5 specific_filter_count:", qs.count())

                elif scope == "broad":
                    expanded_ids = expand_semantic_scope(
                        resolved_concept.semantic_id
                    )
                    print("[QueryFlow] step=5 expanded_ids:", expanded_ids)

                    qs = qs.filter(
                        semantic_concept__semantic_id__in=expanded_ids
                    )
                    print("[QueryFlow] step=5 broad_filter_count:", qs.count())

            except Exception as exc:
                print("[QueryFlow] step=5 semantic_filter_failed:", str(exc))
                reply_text = generate_query_response(
                    user_message,
                    {"event": "query_unsupported"}
                )

                ChatLogs.objects.create(
                    user=user,
                    user_prompt=user_message,
                    ai_response=reply_text,
                )

                return Response({"reply": reply_text})

        # 6) Execute query logic
        if query_type == "aggregate" and metric == "total_spent":
            total = qs.aggregate(total=Sum("amount"))["total"] or 0
            print("[QueryFlow] step=6 branch=aggregate total:", total)

            event_data = {
                "event": "query_result",
                "query_type": "aggregate",
                "metric": "total_spent",
                "amount": float(total),
                "currency": "INR",
                "semantic_concept": semantic,
                "time_range": time_range,
            }

        elif query_type == "list":
            records = qs.order_by("-spent_at")
            print("[QueryFlow] step=6 branch=list count:", records.count())

            event_data = {
                "event": "query_result",
                "query_type": "list",
                "records": [
                    {
                        "item": r.raw_label,
                        "amount": float(r.amount),
                        "spent_at": r.spent_at.isoformat(),
                        "semantic_concept": r.semantic_concept.semantic_id,
                    }
                    for r in records
                ],
                "semantic_concept": semantic,
                "time_range": time_range,
            }

        elif query_type == "boolean" and metric == "spent_any":
            exists = qs.exists()
            print("[QueryFlow] step=6 branch=boolean exists:", exists)

            event_data = {
                "event": "query_result",
                "query_type": "boolean",
                "metric": "spent_any",
                "result": exists,
                "semantic_concept": semantic,
                "time_range": time_range,
            }

        else:
            event_data = {"event": "query_unsupported"}
            print("[QueryFlow] step=6 branch=unsupported")

        print("[QueryFlow] step=6 event_data:", event_data)

        # 7) Generate natural language reply
        reply_text = generate_query_response(user_message, event_data)

        # 8) Save ChatLog
        ChatLogs.objects.create(
            user=user,
            user_prompt=user_message,
            ai_response=reply_text,
        )

        # 9) Return response
        print("[QueryFlow] step=9 reply:", reply_text)
        return Response({"reply": reply_text}, status=status.HTTP_200_OK)

    def handle_chitchat(self, user, user_message): 
        reply_text = generate_chitchat_response(user_message) 
        
        ChatLogs.objects.create( user=user, user_prompt=user_message, ai_response=reply_text ) 
        return Response( {"reply": reply_text}, status=status.HTTP_200_OK )

    def handle_greeting(self, user, user_message):
        reply_text = generate_greeting_response(user_message)
        ChatLogs.objects.create(
            user=user,
            user_prompt=user_message,
            ai_response=reply_text,
        )
        return Response({"reply": reply_text}, status=status.HTTP_200_OK)

