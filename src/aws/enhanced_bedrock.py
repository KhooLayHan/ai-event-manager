import json
import logging
from typing import Dict, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from src.shared_models import SimulationMetrics, SimulationParameters

logger = logging.getLogger(__name__)

def get_dynamic_ai_analysis(before_metrics: SimulationMetrics, params: SimulationParameters) -> Dict:
    """
    Use AWS Bedrock to analyze simulation results and provide recommendations.
    Implements the dynamic prompt template from the master plan.
    """
    try:
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            config=Config(retries={"max_attempts": 3})
        )
        
        # Dynamic prompt template as specified in master plan
        prompt = f"""You are an expert event safety analyst. A crowd simulation for an 'Entry Rush' scenario produced the following results:
- Number of Attendees: {params.attendees}
- Number of Open Gates: {params.open_gates}
- Peak Congestion: {before_metrics.peak_congestion_percent * 100:.1f}%
- Average Wait Time: {before_metrics.avg_wait_time_mins} minutes

Based ONLY on this data, provide a clear, actionable recommendation in a 'recommendation' field. Then, provide a new set of simulation parameters as a JSON object in a 'parameters' field that would likely improve this situation.

Respond in a single, valid JSON format with the keys "recommendation" and "parameters".

Example format:
{{
    "recommendation": "Open additional gates and deploy more staff to reduce congestion and wait times.",
    "parameters": {{
        "recommended_open_gates": 4,
        "recommended_staff": 30,
        "staggered_entry": true
    }}
}}"""

        request_body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.3,
                "topP": 0.9
            }
        }

        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            body=json.dumps(request_body)
        )

        response_body = json.loads(response["body"].read())
        result_text = response_body["results"][0]["outputText"].strip()

        try:
            ai_response = json.loads(result_text)
            return ai_response
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return get_fallback_recommendation(before_metrics, params)

    except Exception as e:
        logger.error(f"Error calling Bedrock: {e}")
        return get_fallback_recommendation(before_metrics, params)

def get_fallback_recommendation(metrics: SimulationMetrics, params: SimulationParameters) -> Dict:
    """Provide intelligent fallback recommendations when AI is unavailable"""
    
    # Calculate recommended gates based on congestion
    current_gates = params.open_gates
    congestion_level = metrics.peak_congestion_percent
    
    if congestion_level > 0.7:  # High congestion
        recommended_gates = min(current_gates + 2, 6)
        recommendation = f"Critical congestion detected ({congestion_level*100:.1f}%). Open {recommended_gates} gates immediately and deploy additional staff to manage crowd flow."
    elif congestion_level > 0.4:  # Medium congestion
        recommended_gates = current_gates + 1
        recommendation = f"Moderate congestion detected. Open {recommended_gates} gates and implement staggered entry to reduce wait times."
    else:  # Low congestion
        recommended_gates = current_gates
        recommendation = "Current gate configuration is adequate. Monitor crowd density and be prepared to open additional gates if needed."
    
    return {
        "recommendation": recommendation,
        "parameters": {
            "recommended_open_gates": recommended_gates,
            "recommended_staff": min(20 + int(congestion_level * 20), 40),
            "staggered_entry": congestion_level > 0.5
        }
    }