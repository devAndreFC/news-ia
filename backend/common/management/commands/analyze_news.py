"""
Comando Django para análise automática de sentimentos e entidades em notícias
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from common.models import News
from common.services import NewsAnalysisService


class Command(BaseCommand):
    help = 'Analisa sentimentos e entidades das notícias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Analisar todas as notícias (reanalisa mesmo as já processadas)'
        )
        
        parser.add_argument(
            '--ids',
            nargs='+',
            type=int,
            help='IDs específicos de notícias para analisar'
        )
        
        parser.add_argument(
            '--category',
            type=str,
            help='Analisar apenas notícias de uma categoria específica'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            help='Analisar notícias dos últimos N dias'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Tamanho do lote para processamento (padrão: 100)'
        )
        
        parser.add_argument(
            '--classify-categories',
            action='store_true',
            help='Executar classificação automática de categorias'
        )
        
        parser.add_argument(
            '--auto-assign-categories',
            action='store_true',
            help='Atribuir automaticamente categorias com alta confiança'
        )
        
        parser.add_argument(
            '--confidence-threshold',
            type=float,
            default=0.3,
            help='Limite de confiança para auto-atribuição de categorias (padrão: 0.3)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando análise de notícias...')
        )
        
        try:
            # Importar modelos
            from common.models import News, Category
            from common.services import NewsAnalysisService
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Q
            
            # Determinar quais notícias analisar
            queryset = self._get_news_queryset(options)
            
            if not queryset.exists():
                self.stdout.write(
                    self.style.WARNING('Nenhuma notícia encontrada para análise.')
                )
                return
            
            total_count = queryset.count()
            self.stdout.write(f'Encontradas {total_count} notícias para análise.')
            
            # Processar em lotes
            batch_size = options['batch_size']
            analysis_service = NewsAnalysisService()
            
            total_success = 0
            total_errors = 0
            total_classified = 0
            total_auto_assigned = 0
            
            for i in range(0, total_count, batch_size):
                # Converter para lista para evitar problemas com slice
                batch_list = list(queryset[i:i + batch_size])
                self.stdout.write(f'Processando lote {i//batch_size + 1}...')
                
                # Análise de sentimento
                results = analysis_service.batch_analyze_news(batch_list)
                
                total_success += results['processed']
                total_errors += results['errors']
                
                # Classificação de categorias se solicitado
                if options['classify_categories']:
                    self.stdout.write('Executando classificação de categorias...')
                    
                    suggestions = analysis_service.suggest_categories_for_news_batch(batch_list)
                    total_classified += len(suggestions)
                    
                    # Auto-atribuir categorias se solicitado
                    if options['auto_assign_categories']:
                        confidence_threshold = options['confidence_threshold']
                        
                        for suggestion in suggestions:
                            classification = suggestion['classification']
                            
                            if (classification['confidence'] >= confidence_threshold and 
                                suggestion['category_object']):
                                
                                try:
                                    news = News.objects.get(id=suggestion['news_id'])
                                    news.category = suggestion['category_object']
                                    news.save()
                                    total_auto_assigned += 1
                                    
                                    self.stdout.write(
                                        f"Auto-atribuída categoria '{classification['suggested_category']}' "
                                        f"para notícia {news.id} (confiança: {classification['confidence']:.1%})"
                                    )
                                except Exception as e:
                                    self.stdout.write(
                                        self.style.ERROR(
                                            f"Erro ao auto-atribuir categoria para notícia {suggestion['news_id']}: {e}"
                                        )
                                    )
                
                # Mostrar erros se houver
                if results['error_details']:
                    for error in results['error_details'][:3]:  # Mostrar apenas os primeiros 3
                        self.stdout.write(
                            self.style.ERROR(
                                f'Erro na notícia {error["news_id"]}: {error["error"]}'
                            )
                        )
            
            # Resumo final
            summary = (
                f'\\nAnálise concluída!\\n'
                f'Total processado: {total_count}\\n'
                f'Sucessos: {total_success}\\n'
                f'Erros: {total_errors}'
            )
            
            if options['classify_categories']:
                summary += (
                    f'\\n\\nClassificação de categorias:\\n'
                    f'Total classificado: {total_classified}'
                )
                
                if options['auto_assign_categories']:
                    summary += f'\\nCategorias auto-atribuídas: {total_auto_assigned}'
            
            self.stdout.write(self.style.SUCCESS(summary))
            
        except Exception as e:
            raise CommandError(f'Erro durante a análise: {str(e)}')

    def _get_news_queryset(self, options):
        """Determina o queryset de notícias baseado nas opções"""
        queryset = News.objects.all()
        
        # Filtrar por IDs específicos
        if options['ids']:
            queryset = queryset.filter(id__in=options['ids'])
            return queryset
        
        # Filtrar por categoria
        if options['category']:
            queryset = queryset.filter(category__name__icontains=options['category'])
        
        # Filtrar por dias
        if options['days']:
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=options['days'])
            queryset = queryset.filter(created_at__gte=cutoff_date)
        
        # Se não for --all, filtrar apenas não analisadas
        if not options['all']:
            queryset = queryset.filter(analysis_timestamp__isnull=True)
        
        return queryset.order_by('created_at')