import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.pipeline.stage_2_refinery.schemas import AnalysisOutput

class ClaudeClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0,
            api_key=api_key
        )
        self.parser = PydanticOutputParser(pydantic_object=AnalysisOutput)

    async def analyze_submission(self, prompt_text: str) -> AnalysisOutput:
        """
        Sends the prompt to Claude and returns the structured analysis.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful coding assistant."),
            ("user", "{input}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = await chain.ainvoke({"input": prompt_text})
            return result
        except Exception as e:
            # Simple retry or error handling could be added here
            print(f"Error calling Claude: {e}")
            raise e
