import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import logging

from loguru import logger

logger.add(
    "logs/sebi.log",
    rotation="500 MB",
    retention="10 days",
    format="{time} | {level: <8} | {name}:{function}:{line} - {message}"
)

class RequestState(str, Enum):
    """Request processing states"""
    RECEIVED = "received"
    VALIDATED = "validated"
    INTENT_DETECTED = "intent_detected"
    CONTEXT_COLLECTED = "context_collected"
    KNOWLEDGE_RETRIEVED = "knowledge_retrieved"
    REASONING = "reasoning"
    TOOL_SELECTED = "tool_selected"
    SOURCE_ROUTED = "source_routed"
    VERIFICATION = "verification"
    SYNTHESIS = "synthesis"
    QUALITY_CHECK = "quality_check"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class RequestContext:
    """Context for processing a request through SEBI pipeline"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    user_message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    state: RequestState = RequestState.RECEIVED
    
    # Pipeline results
    intent: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    retrieved_knowledge: List[Dict[str, Any]] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    selected_tools: List[str] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    verification_results: Dict[str, Any] = field(default_factory=dict)
    final_response: Optional[str] = None
    confidence_score: float = 0.0
    
    # Metadata
    reasoning_effort: str = "medium"
    model_version: str = "v1"
    dataset_version: str = "v1"
    execution_time_ms: float = 0.0
    error: Optional[str] = None

class SEBIController:
    """Core SEBI Controller - Orchestrates the entire pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logger.bind(name="SEBIController")
        self.request_history: Dict[str, RequestContext] = {}
        self.reasoning_engine = None
        self.knowledge_base = None
        self.verification_engine = None
        self.tool_executor = None
        self.external_connectors = {}
        
    async def process_request(self, user_message: str, user_id: Optional[str] = None,
                             reasoning_effort: str = "medium") -> RequestContext:
        """Main pipeline: Process user request through SEBI stages"""
        
        context = RequestContext(
            user_message=user_message,
            user_id=user_id,
            reasoning_effort=reasoning_effort
        )
        
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Processing request {context.request_id}")
            
            # Stage 1: Input Validation
            context.state = RequestState.VALIDATED
            if not await self._validate_input(context):
                context.error = "Input validation failed"
                raise ValueError("Invalid input")
            
            # Stage 2: Intent Detection
            context.state = RequestState.INTENT_DETECTED
            context.intent = await self._detect_intent(context)
            self.logger.debug(f"Detected intent: {context.intent}")
            
            # Stage 3: Context Collection
            context.state = RequestState.CONTEXT_COLLECTED
            context.context_data = await self._collect_context(context)
            
            # Stage 4: Knowledge Retrieval
            context.state = RequestState.KNOWLEDGE_RETRIEVED
            context.retrieved_knowledge = await self._retrieve_knowledge(context)
            
            # Stage 5: Reasoning
            if self.reasoning_engine:
                context.state = RequestState.REASONING
                context.reasoning_steps = await self._perform_reasoning(context)
            
            # Stage 6: Tool Selection
            context.state = RequestState.TOOL_SELECTED
            context.selected_tools = await self._select_tools(context)
            
            # Stage 7: Source Routing
            context.state = RequestState.SOURCE_ROUTED
            context.sources_used = await self._route_sources(context)
            
            # Stage 8: Verification
            context.state = RequestState.VERIFICATION
            context.verification_results = await self._verify_information(context)
            
            # Stage 9: Synthesis
            context.state = RequestState.SYNTHESIS
            context.final_response = await self._synthesize_response(context)
            
            # Stage 10: Quality Check
            context.state = RequestState.QUALITY_CHECK
            quality_passed = await self._quality_check(context)
            
            if quality_passed:
                context.state = RequestState.COMPLETE
                context.confidence_score = await self._calculate_confidence(context)
            else:
                context.error = "Quality check failed"
                context.state = RequestState.FAILED
            
            # Calculate execution time
            context.execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Store in history
            self.request_history[context.request_id] = context
            
            self.logger.info(f"Request {context.request_id} completed in {context.execution_time_ms:.2f}ms")
            
            return context
            
        except Exception as e:
            context.state = RequestState.FAILED
            context.error = str(e)
            context.execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.logger.error(f"Request {context.request_id} failed: {e}")
            self.request_history[context.request_id] = context
            return context
    
    async def _validate_input(self, context: RequestContext) -> bool:
        """Validate user input"""
        if not context.user_message or len(context.user_message.strip()) == 0:
            return False
        if len(context.user_message) > 10000:
            return False
        return True
    
    async def _detect_intent(self, context: RequestContext) -> str:
        """Detect user intent from message"""
        # Simplified intent detection
        message_lower = context.user_message.lower()
        if any(word in message_lower for word in ["search", "find", "look for"]):
            return "search"
        elif any(word in message_lower for word in ["explain", "describe", "tell me"]):
            return "explain"
        elif any(word in message_lower for word in ["code", "write", "generate"]):
            return "generate"
        elif any(word in message_lower for word in ["debug", "error", "wrong"]):
            return "debug"
        else:
            return "general_query"
    
    async def _collect_context(self, context: RequestContext) -> Dict[str, Any]:
        """Collect contextual information"""
        return {
            "user_id": context.user_id,
            "timestamp": context.timestamp.isoformat(),
            "reasoning_effort": context.reasoning_effort
        }
    
    async def _retrieve_knowledge(self, context: RequestContext) -> List[Dict[str, Any]]:
        """Retrieve knowledge from knowledge base"""
        if not self.knowledge_base:
            return []
        
        try:
            retrieved = await self.knowledge_base.retrieve(
                query=context.user_message,
                top_k=self.config.top_k_retrieval,
                threshold=self.config.similarity_threshold
            )
            return retrieved
        except Exception as e:
            self.logger.warning(f"Knowledge retrieval failed: {e}")
            return []
    
    async def _perform_reasoning(self, context: RequestContext) -> List[str]:
        """Perform multi-stage reasoning"""
        if not self.reasoning_engine:
            return []
        
        try:
            steps = await self.reasoning_engine.reason(
                query=context.user_message,
                context=context.context_data,
                retrieved_knowledge=context.retrieved_knowledge,
                reasoning_effort=context.reasoning_effort
            )
            return steps
        except Exception as e:
            self.logger.warning(f"Reasoning failed: {e}")
            return []
    
    async def _select_tools(self, context: RequestContext) -> List[str]:
        """Select appropriate tools for the task"""
        selected = []
        if context.intent == "search":
            selected.append("web_search")
            selected.append("knowledge_retrieval")
        elif context.intent == "generate":
            selected.append("code_generator")
        elif context.intent == "debug":
            selected.append("error_analyzer")
            selected.append("debugging_tool")
        return selected
    
    async def _route_sources(self, context: RequestContext) -> List[str]:
        """Route to appropriate information sources"""
        sources = ["internal_knowledge"]
        
        if context.retrieved_knowledge:
            sources.append("retrieved_knowledge")
        
        if self.config.web_search_enabled and context.intent in ["search", "general_query"]:
            sources.append("web_search")
        
        if self.config.training_enabled and len(context.reasoning_steps) > 3:
            sources.append("trained_model")
        
        return sources
    
    async def _verify_information(self, context: RequestContext) -> Dict[str, Any]:
        """Verify retrieved and generated information"""
        if not self.verification_engine:
            return {"verified": False, "confidence": 0.0}
        
        try:
            results = await self.verification_engine.verify(
                sources=context.sources_used,
                retrieved_knowledge=context.retrieved_knowledge,
                reasoning_steps=context.reasoning_steps
            )
            return results
        except Exception as e:
            self.logger.warning(f"Verification failed: {e}")
            return {"verified": False, "confidence": 0.0}
    
    async def _synthesize_response(self, context: RequestContext) -> str:
        """Synthesize final response"""
        # This would integrate with the LLM
        if context.intent == "search":
            return f"Based on {len(context.retrieved_knowledge)} retrieved sources..."
        elif context.intent == "explain":
            return "Here's an explanation based on the available knowledge..."
        elif context.intent == "generate":
            return "Generated code/content..."
        else:
            return "Response synthesized from multiple sources"
    
    async def _quality_check(self, context: RequestContext) -> bool:
        """Perform quality checks on the response"""
        if not context.final_response:
            return False
        if len(context.final_response) < 10:
            return False
        return True
    
    async def _calculate_confidence(self, context: RequestContext) -> float:
        """Calculate confidence score for the response"""
        score = 0.5  # Base score
        
        if context.retrieved_knowledge:
            score += 0.1 * min(len(context.retrieved_knowledge) / 5, 1.0)
        
        if context.verification_results.get("verified"):
            score += 0.2
        
        if len(context.reasoning_steps) > 0:
            score += 0.1
        
        if len(context.sources_used) > 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def get_request_history(self, user_id: Optional[str] = None) -> List[RequestContext]:
        """Get request history"""
        if user_id:
            return [ctx for ctx in self.request_history.values() if ctx.user_id == user_id]
        return list(self.request_history.values())
