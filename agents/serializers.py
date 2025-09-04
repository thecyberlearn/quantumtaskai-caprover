from rest_framework import serializers
from .models import AgentExecution

class AgentExecutionSerializer(serializers.ModelSerializer):
    # Agent data comes from files via AgentFileService
    
    class Meta:
        model = AgentExecution
        fields = [
            'id', 'agent_slug', 'agent_name', 'input_data', 'output_data', 'status',
            'fee_charged', 'error_message', 'execution_time',
            'created_at', 'completed_at'
        ]