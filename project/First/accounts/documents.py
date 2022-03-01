from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import History


@registry.register_document
class HistoryDocument(Document):
    class Index:
        name = 'history'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = History
        fields = [
            'user_id',
            'ip',
            'browser'
        ]
