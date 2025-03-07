from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

async def translate_and_summarize(content: str, source_lang: str, target_lang: str) -> str:
    llm = OpenAI(temperature=0.7)
    
    prompt_template = """
    Please translate and summarize the following text from {source_lang} to {target_lang}:
    
    {content}
    
    Provide a concise summary in {target_lang}.
    """
    
    prompt = PromptTemplate(
        input_variables=["content", "source_lang", "target_lang"],
        template=prompt_template
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    
    result = chain.run({
        "content": content,
        "source_lang": source_lang,
        "target_lang": target_lang
    })
    
    return result
