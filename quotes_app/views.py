from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.urls import reverse_lazy
from .forms import QuoteForm
from .models import Quote
import random
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

class QuoteCreateView(CreateView):
    form_class = QuoteForm
    template_name = 'quotes_app/add_quote.html'
    success_url = reverse_lazy('home')

class HomeView(TemplateView):
    template_name = 'quotes_app/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quotes = Quote.objects.all()
        if quotes.exists():
            quote = random.choices(
                quotes,
                weights=[quote.weight for quote in quotes],
                k=1
            )[0]
            quote.views += 1
            quote.save()
            context['quote'] = quote
            voted_quotes = self.request.session.get('voted_quotes', {})
            if isinstance(voted_quotes, list):
                voted_quotes = {str(qid): 'like' for qid in voted_quotes}
                self.request.session['voted_quotes'] = voted_quotes
                self.request.session.modified = True
            context['user_vote'] = voted_quotes.get(str(quote.id), '')
        else:
            context['quote'] = None
            context['user_vote'] = ''
        return context

class LikeDislikeView(View):
    def post(self, request):
        try:
            quote_id = request.POST.get('quote_id')
            action = request.POST.get('action')
            if not quote_id or not action:
                return JsonResponse({'status': 'error', 'message': 'Missing quote_id or action'}, status=400)
            
            quote = Quote.objects.get(id=quote_id)
            voted_quotes = request.session.get('voted_quotes', {})
            if isinstance(voted_quotes, list):
                voted_quotes = {str(qid): 'like' for qid in voted_quotes}
                request.session['voted_quotes'] = voted_quotes
                request.session.modified = True
            
            previous_action = voted_quotes.get(quote_id)
            current_action = None
            
            if previous_action == action:
                if action == 'like':
                    quote.likes = max(0, quote.likes - 1)
                elif action == 'dislike':
                    quote.dislikes = max(0, quote.dislikes - 1)
                voted_quotes.pop(quote_id, None)
            else:
                if previous_action:
                    if previous_action == 'like':
                        quote.likes = max(0, quote.likes - 1)
                    elif previous_action == 'dislike':
                        quote.dislikes = max(0, quote.dislikes - 1)
                
                if action == 'like':
                    quote.likes += 1
                    current_action = 'like'
                elif action == 'dislike':
                    quote.dislikes += 1
                    current_action = 'dislike'
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
                
                voted_quotes[quote_id] = action
            
            quote.save()
            request.session['voted_quotes'] = voted_quotes
            request.session.modified = True
            
            return JsonResponse({
                'status': 'success',
                'likes': quote.likes,
                'dislikes': quote.dislikes,
                'voted_action': current_action
            })
        except Quote.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Quote not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)

class QuoteListView(TemplateView):
    """Базовый класс для отображения списка цитат."""
    template_name = None
    sort_field = None
    limit = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quotes = Quote.objects.all().order_by(f'-{self.sort_field}')[:self.limit]
        voted_quotes = self.request.session.get('voted_quotes', {})
        if isinstance(voted_quotes, list):
            voted_quotes = {str(qid): 'like' for qid in voted_quotes}
            self.request.session['voted_quotes'] = voted_quotes
            self.request.session.modified = True
        for quote in quotes:
            quote.user_vote = voted_quotes.get(str(quote.id), '')
        context['quotes'] = quotes
        return context

class TopQuotesView(QuoteListView):
    """Отображение топ-10 цитат по лайкам."""
    template_name = 'quotes_app/top_quotes.html'
    sort_field = 'likes'

class WorstQuotesView(QuoteListView):
    """Отображение худших 10 цитат по дизлайкам."""
    template_name = 'quotes_app/worst_quotes.html'
    sort_field = 'dislikes'

class DeleteQuoteView(View):
    def post(self, request):
        try:
            quote_id = request.POST.get('quote_id')
            logger.debug(f"Received delete request for quote_id: {quote_id}")
            if not quote_id:
                logger.error("Missing quote_id in request")
                return JsonResponse({'status': 'error', 'message': 'Missing quote_id'}, status=400)
            
            quote = Quote.objects.get(id=quote_id)
            logger.info(f"Deleting quote: {quote.text} (ID: {quote_id})")
            quote.delete()
            
            # Удаляем голос для этой цитаты из сессии
            voted_quotes = request.session.get('voted_quotes', {})
            if isinstance(voted_quotes, list):
                voted_quotes = {str(qid): 'like' for qid in voted_quotes}
            voted_quotes.pop(str(quote_id), None)
            request.session['voted_quotes'] = voted_quotes
            request.session.modified = True
            logger.debug(f"Updated session: voted_quotes = {voted_quotes}")
            
            # Получаем новую цитату
            quotes = Quote.objects.all()
            new_quote = None
            if quotes.exists():
                new_quote = random.choices(
                    quotes,
                    weights=[quote.weight for quote in quotes],
                    k=1
                )[0]
                new_quote.views += 1
                new_quote.save()
                logger.info(f"Selected new quote: {new_quote.text} (ID: {new_quote.id})")
            
            response_data = {
                'status': 'success',
                'new_quote': {
                    'id': new_quote.id if new_quote else None,
                    'text': new_quote.text if new_quote else '',
                    'source': new_quote.source.name if new_quote else '',
                    'likes': new_quote.likes if new_quote else 0,
                    'dislikes': new_quote.dislikes if new_quote else 0,
                    'views': new_quote.views if new_quote else 0,
                    'user_vote': voted_quotes.get(str(new_quote.id), '') if new_quote else ''
                } if new_quote else None,
                'message': 'Цитата удалена' if new_quote else 'Цитата удалена, новых цитат нет'
            }
            logger.debug(f"Response data: {response_data}")
            return JsonResponse(response_data)
        except Quote.DoesNotExist:
            logger.error(f"Quote not found: {quote_id}")
            return JsonResponse({'status': 'error', 'message': 'Quote not found'}, status=404)
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from .models import Quote

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    quote.delete()
    return redirect('home')
