from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import pandas as pd
import os
import time
import json
import re

os.environ['GROQ_API_KEY'] = ''

chat = ChatGroq(
    temperature=0,
    model_name="groq/mixtral-8x7b-32768"
)

quality_agent = Agent(
    role="Quality Assessment Agent",
    goal="Evaluate the quality of survey responses",
    backstory="You assign a quality score based on completeness and meaningfulness.",
    verbose=False,
    allow_delegation=False,
    llm=chat
)

quality_task = Task(
    description="""
    Evaluate the survey response:
    {text}

    Assign a quality score:
    - 0 if poor (empty, generic, gibberish).
    - 1 if acceptable.

    Return ONLY the following JSON with no explanations:
    {{"quality_score": <0 or 1>}}
    """,
    agent=quality_agent,
    expected_output="JSON with quality score only"
)

context_relevance_agent = Agent(
    role="Context Relevance Analyst",
    goal="Evaluate how relevant survey responses are to the specific questions",
    backstory="You analyze whether responses address the questions asked.",
    verbose=False,
    allow_delegation=False,
    llm=chat
)

context_relevance_task = Task(
    description="""
    Analyze the relevance of this survey response to the question asked:
    
    Survey Context: {survey_context}
    Question: {question_text}
    Response: {text}
    
    Assign a relevance score:
    - Score 0: Not relevant
    - Score 1: Barely relevant
    - Score 2: Mostly relevant
    - Score 3: Highly relevant
    
    Return ONLY the following JSON with no explanations:
    {{"relevance_score": <0-3>}}
    """,
    agent=context_relevance_agent,
    expected_output="JSON with relevance score only"
)

sentiment_toxicity_agent = Agent(
    role="Sentiment & Toxicity Analyst",
    goal="Evaluate sentiment and detect harmful language",
    backstory="You analyze sentiment and content moderation.",
    verbose=False,
    allow_delegation=False,
    llm=chat
)

sentiment_toxicity_task = Task(
    description="""
    Analyze the sentiment and check for toxic content:
    
    Response: {text}
    
    Return ONLY the following JSON with no explanations:
    {{
        "sentiment": "<positive/neutral/negative>",
        "contains_toxic_content": <true/false>,
        "sentiment_toxicity_score": <-2 to 2>
    }}
    """,
    agent=sentiment_toxicity_agent,
    expected_output="JSON with sentiment and toxicity data only"
)

product_replacement_agent = Agent(
    role="Brand Checker Agent",
    goal="Evaluate if mentioned product is an alcoholic beverage or an alcoholic brand name",
    backstory="You assess whether the is an alcoholic beverage or an alcoholic brand name.",
    verbose=False,
    allow_delegation=False,
    llm=chat
)

product_replacement_task = Task(
    description="""
    Evaluate if this product mentioned could reasonably be replaced by the concept described:
    
    Survey Context: {survey_context}
    Question: {question_text}
    Response: {text}
    
    Assign a relevance score:
    - Score 0: Not relevant
    - Score 1: Relevant, that means the response is an alcoholic beverage or an alcoholic brand name
    
    Return ONLY the following JSON with no explanations:
    {{"replacement_relevance": <0 or 1>}}
    """,
    agent=product_replacement_agent,
    expected_output="JSON with replacement relevance score only"
)

quality_crew = Crew(
    agents=[quality_agent],
    tasks=[quality_task],
    verbose=False,
    process=Process.sequential
)

context_crew = Crew(
    agents=[context_relevance_agent],
    tasks=[context_relevance_task],
    verbose=False,
    process=Process.sequential
)

sentiment_toxicity_crew = Crew(
    agents=[sentiment_toxicity_agent],
    tasks=[sentiment_toxicity_task],
    verbose=False,
    process=Process.sequential
)

product_replacement_crew = Crew(
    agents=[product_replacement_agent],
    tasks=[product_replacement_task],
    verbose=False,
    process=Process.sequential
)

def extract_json_from_text(text):
    if not text:
        return {}
    
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, text)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    json_object_pattern = r'(\{[\s\S]*\})'
    matches = re.findall(json_object_pattern, text)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return {}

def process_survey_responses(csv_path, survey_context, output_path, backup_dir):
    df = pd.read_csv(csv_path)

    required_columns = ['Q16A', 'Q16B']
    q18_columns = ['Q18_1', 'Q18_2', 'Q18_3']
    
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"CSV must contain '{col}' column.")
    
    for col in q18_columns:
        if col not in df.columns:
            raise ValueError(f"CSV must contain '{col}' column.")

    q16a_text = "What is the most important thing you LIKE about the shown concept? This can include anything you would want kept for sure or aspects that might drive you to buy or try it."
    q16b_text = "What is the most important thing you DISLIKE about the shown concept? This can include general concerns, annoyances, or any aspects of the product that need fixed for this to be more appealing to you."
    q18_1_text = "What specific product that you are currently using would the shown product replace? Please type in ONE specific brand or product per space provided."
    q18_2_text = "What specific product that you are currently using would the shown concept replace? Please type in ONE specific brand or product per space provided."
    q18_3_text = "What specific product that you are currently using would the shown concept replace? Please type in ONE specific brand or product per space provided."

    q18_question_texts = {
        'Q18_1': q18_1_text,
        'Q18_2': q18_2_text,
        'Q18_3': q18_3_text
    }

    df['Q16A_Quality'] = 0
    df['Q16A_Relevance'] = 0
    df['Q16A_Sentiment'] = ""
    df['Q16A_Toxic'] = False
    df['Q16A_SentimentScore'] = 0
    
    df['Q16B_Quality'] = 0
    df['Q16B_Relevance'] = 0
    df['Q16B_Sentiment'] = ""
    df['Q16B_Toxic'] = False
    df['Q16B_SentimentScore'] = 0
    
    for col in q18_columns:
        df[f'{col}_Relevance'] = 0
    
    df['Total_Quality_Score'] = 0
    df['Total_Relevance_Score'] = 0
    df['Total_Sentiment_Score'] = 0
    df['Total_Q18_Relevance_Score'] = 0
    df['Combined_Total_Score'] = 0
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")

    last_processed_row = -1
    
    recovery_file = os.path.join(backup_dir, "recovery_info.json")
    if os.path.exists(recovery_file):
        try:
            with open(recovery_file, 'r') as f:
                recovery_data = json.load(f)
                last_processed_row = recovery_data.get("last_processed_row", -1)
                print(f"Recovery file found. Starting from row {last_processed_row + 1}")
        except Exception as e:
            print(f"Warning: Could not read recovery file: {str(e)}")

    for idx, row in df.iterrows():
        if idx <= last_processed_row:
            print(f"Skipping already processed row {idx}...")
            continue
            
        print(f"Processing row {idx}...")
        
        total_quality = 0
        total_relevance = 0
        total_sentiment = 0
        total_q18_relevance = 0

        for col, question_text in [('Q16A', q16a_text), ('Q16B', q16b_text)]:
            if pd.notna(row[col]) and isinstance(row[col], str) and len(row[col].strip()) > 0:
                try:
                    text = row[col].strip()
                    
                    quality_result = quality_crew.kickoff(inputs={"text": text})
                    quality_data = extract_json_from_text(quality_result.raw) if hasattr(quality_result, 'raw') else {}
                    quality_score = int(quality_data.get('quality_score', 0))
                    
                    df.at[idx, f'{col}_Quality'] = quality_score
                    total_quality += quality_score
                    
                    context_result = context_crew.kickoff(inputs={
                        "survey_context": survey_context,
                        "question_text": question_text,
                        "text": text
                    })
                    
                    context_data = extract_json_from_text(context_result.raw) if hasattr(context_result, 'raw') else {}
                    relevance_score = int(context_data.get('relevance_score', 0))
                    
                    df.at[idx, f'{col}_Relevance'] = relevance_score
                    total_relevance += relevance_score
                    
                    sentiment_result = sentiment_toxicity_crew.kickoff(inputs={"text": text})
                    
                    sentiment_data = extract_json_from_text(sentiment_result.raw) if hasattr(sentiment_result, 'raw') else {}
                    sentiment = sentiment_data.get('sentiment', 'neutral')
                    is_toxic = sentiment_data.get('contains_toxic_content', False)
                    sentiment_score = int(sentiment_data.get('sentiment_toxicity_score', 0))
                    
                    df.at[idx, f'{col}_Sentiment'] = sentiment
                    df.at[idx, f'{col}_Toxic'] = is_toxic
                    df.at[idx, f'{col}_SentimentScore'] = sentiment_score
                    total_sentiment += sentiment_score
                
                except Exception as e:
                    print(f"Error processing {col} for row {idx}: {str(e)}")
            
            else:
                print(f"Skipping {col} for row {idx} - empty or invalid")
        
        for col in q18_columns:
            question_text = q18_question_texts[col]
            
            if pd.notna(row[col]) and isinstance(row[col], str) and len(row[col].strip()) > 0:
                try:
                    text = row[col].strip()
                    
                    replacement_result = product_replacement_crew.kickoff(inputs={
                        "survey_context": survey_context,
                        "question_text": question_text,
                        "text": text
                    })
                    
                    replacement_data = extract_json_from_text(replacement_result.raw) if hasattr(replacement_result, 'raw') else {}
                    replacement_score = int(replacement_data.get('replacement_relevance', 0))
                    
                    df.at[idx, f'{col}_Relevance'] = replacement_score
                    total_q18_relevance += replacement_score
                
                except Exception as e:
                    print(f"Error processing {col} for row {idx}: {str(e)}")
            
            else:
                print(f"Skipping {col} for row {idx} - empty or invalid")
                df.at[idx, f'{col}_Relevance'] = 0
        
        df.at[idx, 'Total_Quality_Score'] = total_quality
        df.at[idx, 'Total_Relevance_Score'] = total_relevance
        df.at[idx, 'Total_Sentiment_Score'] = total_sentiment
        df.at[idx, 'Total_Q18_Relevance_Score'] = total_q18_relevance
        
        df.at[idx, 'Combined_Total_Score'] = total_quality + total_relevance + total_sentiment + total_q18_relevance
        
        backup_filename = f"backup_after_row_{idx}.csv"
        backup_path = os.path.join(backup_dir, backup_filename)
        df.to_csv(backup_path, index=False)
        print(f"Saved backup to {backup_path}")
        
        df.to_csv(output_path, index=False)
        print(f"Updated main output file: {output_path}")
        
        with open(recovery_file, 'w') as f:
            json.dump({"last_processed_row": idx}, f)
        
        print(f"Completed row {idx}, waiting before next row...")
        time.sleep(15)

    return df

def main(csv_path, survey_context, output_path=None, summary_path=None):
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    backup_dir = f"{base_name}_backups"
    
    if output_path is None:
        output_path = f"{os.path.splitext(csv_path)[0]}_processed_with_scores.csv"
    
    if summary_path is None:
        summary_path = f"{os.path.splitext(csv_path)[0]}_combined_scores.csv"

    try:
        processed_df = process_survey_responses(csv_path, survey_context, output_path, backup_dir)
        processed_df.to_csv(output_path, index=False)
        print(f"Processing complete. Results saved to {output_path}")
        
        summary_df = processed_df[['Total_Quality_Score', 'Total_Relevance_Score', 'Total_Sentiment_Score', 
                                  'Total_Q18_Relevance_Score', 'Combined_Total_Score']]
        summary_df.to_csv(summary_path, index=False)
        print(f"Combined scores summary saved to {summary_path}")
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    csv_file_path = ""



    # Survey Context can be changed based on the Problem Domain.
    survey_context = """
    [The image contains an advertisement for Michelob ULTRA Pure Gold, a premium light lager. Key details include: 
    Calories: 85 per serving
    Carbs: 2.5g
    ABV (Alcohol By Volume): 3.8%
    Price: $9.99 for a 6-pack of 12oz bottles
    The description highlights that the beer is brewed with American homegrown ingredients, offering a refreshing taste with low calories and carbs. The tagline suggests it is a "Superior Light Beer for those who go for gold."
    The right side of the image shows a bottle of Michelob ULTRA Pure Gold with a golden label and the brand name prominently displayed.]
    """
    main(csv_file_path, survey_context)