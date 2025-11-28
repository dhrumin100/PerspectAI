from google import genai
from google.genai import types
from app.core.config import Config
from typing import Dict, List, Any, Optional

class SearchService:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.model = Config.SEARCH_MODEL_NAME
        self.tools = [types.Tool(google_search=types.GoogleSearch())]

    def search(self, query: str) -> str:
        """
        Performs a Google Search using the Gemini API and returns the model's synthesis.
        Simple version that returns just the text.
        """
        print(f"DEBUG: Performing search for: {query}")
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=query,
            config=types.GenerateContentConfig(
                tools=self.tools,
                response_modalities=["TEXT"],
            )
        )
        
        return response.text

    def search_with_sources(self, query: str) -> Dict[str, Any]:
        """
        Performs a Google Search and returns both the response text AND extracted sources.
        This uses Gemini's grounded search capability.
        """
        print(f"DEBUG: Performing grounded search for: {query}")
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=query,
            config=types.GenerateContentConfig(
                tools=self.tools,
                response_modalities=["TEXT"],
            )
        )
        
        # Extract text response
        text_response = response.text
        
        # Extract grounding metadata (sources)
        sources = []
        try:
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                # Try to get grounding metadata
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_metadata = candidate.grounding_metadata
                    
                    # Extract grounding chunks (sources)
                    if hasattr(grounding_metadata, 'grounding_chunks') and grounding_metadata.grounding_chunks:
                        for chunk in grounding_metadata.grounding_chunks:
                            source_info = {}
                            
                            # Extract web source information
                            if hasattr(chunk, 'web') and chunk.web:
                                source_info['url'] = getattr(chunk.web, 'uri', '')
                                source_info['title'] = getattr(chunk.web, 'title', '')
                                
                            # Extract chunk text if available
                            if hasattr(chunk, 'text') and chunk.text:
                                source_info['snippet'] = chunk.text[:200]  # First 200 chars
                            
                            if source_info:
                                sources.append(source_info)
                    
                    # Also try grounding_supports (alternative structure)
                    if hasattr(grounding_metadata, 'grounding_supports'):
                        for support in grounding_metadata.grounding_supports:
                            if hasattr(support, 'web_search_result'):
                                result = support.web_search_result
                                source_info = {
                                    'url': getattr(result, 'uri', ''),
                                    'title': getattr(result, 'title', ''),
                                    'snippet': getattr(result, 'snippet', '')
                                }
                                if source_info['url']:
                                    sources.append(source_info)
                    
                    # Get search entry point if available
                    if hasattr(grounding_metadata, 'search_entry_point'):
                        entry_point = grounding_metadata.search_entry_point
                        if hasattr(entry_point, 'rendered_content'):
                            print(f"DEBUG: Search entry point available")
        
        except Exception as e:
            print(f"WARNING: Error extracting grounding metadata: {e}")
        
        # Remove duplicates based on URL
        unique_sources = []
        seen_urls = set()
        for source in sources:
            url = source.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        return {
            'text': text_response,
            'sources': unique_sources,
            'has_grounding': len(unique_sources) > 0
        }

    def chat(self, message: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Chat with context - maintains conversation history.
        Uses grounded search for factual queries.
        """
        # System instruction for the chat
        system_instruction = """You are PerspectAI, an intelligent fact-checking assistant powered by grounded search.

Your capabilities:
- Fact-check claims using real-time web search
- Provide accurate, verified information with sources
- Engage in natural conversation while maintaining factual accuracy
- Clearly indicate when information comes from search vs. general knowledge

Guidelines:
- Always cite sources when using grounded search
- Be conversational but precise
- If you don't know something, say so
- For fact-checking, provide clear verdicts with evidence"""
        
        # Build conversation contents
        contents = []
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg['role'] == 'user' else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg['content'])]
                ))
        
        # Add current message
        contents.append(message)
        
        print(f"DEBUG: Chat request with {len(conversation_history) if conversation_history else 0} history messages")
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=self.tools,  # Grounded search enabled
                response_modalities=["TEXT"],
                system_instruction=system_instruction
            )
        )
        
        # Extract text and sources
        text_response = response.text
        sources = []
        
        # DEBUG: Print full response structure to see what we get
        print(f"DEBUG: Response object type: {type(response)}")
        print(f"DEBUG: Has candidates: {hasattr(response, 'candidates')}")
        if hasattr(response, 'candidates') and response.candidates:
            print(f"DEBUG: Number of candidates: {len(response.candidates)}")
            candidate = response.candidates[0]
            print(f"DEBUG: Candidate has grounding_metadata: {hasattr(candidate, 'grounding_metadata')}")
            if hasattr(candidate, 'grounding_metadata'):
                print(f"DEBUG: Grounding metadata: {candidate.grounding_metadata}")
        
        # Extract grounding metadata
        try:
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_metadata = candidate.grounding_metadata
                    
                    # Try grounding_chunks first
                    if hasattr(grounding_metadata, 'grounding_chunks') and grounding_metadata.grounding_chunks:
                        print(f"DEBUG: Found {len(grounding_metadata.grounding_chunks)} grounding chunks")
                        for chunk in grounding_metadata.grounding_chunks:
                            source_info = {}
                            if hasattr(chunk, 'web') and chunk.web:
                                source_info['url'] = getattr(chunk.web, 'uri', '')
                                source_info['title'] = getattr(chunk.web, 'title', '')
                                print(f"DEBUG: Extracted source: {source_info}")
                            if source_info.get('url'):
                                sources.append(source_info)
                    
                    # Try grounding_supports (alternative structure)
                    if hasattr(grounding_metadata, 'grounding_supports') and grounding_metadata.grounding_supports:
                        print(f"DEBUG: Found {len(grounding_metadata.grounding_supports)} grounding supports")
                        for support in grounding_metadata.grounding_supports:
                            if hasattr(support, 'segment'):
                                segment = support.segment
                                if hasattr(segment, 'text'):
                                    # Extract URL from grounding support
                                    if hasattr(support, 'grounding_chunk_indices'):
                                        print(f"DEBUG: Found grounding support with indices")
                    
                    # Try web_search_queries
                    if hasattr(grounding_metadata, 'web_search_queries'):
                        print(f"DEBUG: Search queries: {grounding_metadata.web_search_queries}")
                    
                    # Try search_entry_point
                    if hasattr(grounding_metadata, 'search_entry_point') and grounding_metadata.search_entry_point:
                        print(f"DEBUG: Has search_entry_point")
                        entry_point = grounding_metadata.search_entry_point
                        # The search entry point might have rendered content with links
                        if hasattr(entry_point, 'rendered_content') and entry_point.rendered_content:
                            print(f"DEBUG: Search entry point rendered content available")
                
                else:
                    print("DEBUG: No grounding metadata found - response may not have used search")
        
        except Exception as e:
            print(f"WARNING: Error extracting sources in chat: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"DEBUG: Total sources extracted: {len(sources)}")
        
        return {
            'response': text_response,
            'sources': sources
        }

