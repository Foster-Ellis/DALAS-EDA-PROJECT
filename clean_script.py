import pandas as pd
import re
import string
from rapidfuzz import fuzz  # RapidFuzz is a fast fuzzy string matching library

# ----------------------------
# Function: preprocess_text
# ----------------------------
def preprocess_text(text: str, stopwords: list = None) -> str:
    """
    Preprocess input text by:
    - Converting to lower case.
    - Removing punctuation.
    - Removing extra whitespace.
    - Removing specified stopwords.
    
    Parameters:
        text (str): The input text string.
        stopwords (list): List of stopwords to remove from text.
        
    Returns:
        str: The cleaned and normalized text.
    """
    # Convert to lower case
    text = text.lower()
    # Remove punctuation using translation table
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove stopwords if provided
    if stopwords:
        # Build regex pattern to match whole words in the stopwords list
        pattern = r'\b(?:' + '|'.join(map(re.escape, stopwords)) + r')\b'
        text = re.sub(pattern, '', text)
        # Remove extra spaces created by stopword removal
        text = re.sub(r'\s+', ' ', text).strip()
    return text

# ----------------------------
# Function: deduplicate_discoveries
# ----------------------------
def deduplicate_discoveries(df: pd.DataFrame, threshold: int = 90) -> pd.DataFrame:
    """
    Deduplicate records based on the 'Name of Scientific Discovery' field using fuzzy matching.
    
    The function preprocesses the discovery names, compares them pairwise using a similarity threshold,
    assigns group IDs for duplicates, and aggregates the groups by combining information from other fields.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame containing the data.
        threshold (int): Similarity threshold (0-100) above which two strings are considered duplicates.
        
    Returns:
        pd.DataFrame: A deduplicated DataFrame with aggregated fields.
    """
    # Define a custom stopwords list - can be modified or extended as needed
    stopwords = ['the', 'for', 'of', 'origin', 'universe', 'theory', 'proposed']
    
    # Create a new column with cleaned 'Name of Scientific Discovery'
    df['cleaned_discovery'] = df['Name of Scientific Discovery'].apply(lambda x: preprocess_text(x, stopwords=stopwords))
    
    # Initialize group IDs for each record as -1 (unassigned)
    n = len(df)
    group_ids = [-1] * n
    current_group = 0
    
    # Compare each record with subsequent records for similarity
    for i in range(n):
        if group_ids[i] != -1:
            continue  # Skip if already assigned to a group
        group_ids[i] = current_group  # Assign current record to a new group
        base_text = df.iloc[i]['cleaned_discovery']
        for j in range(i + 1, n):
            if group_ids[j] != -1:
                continue
            compare_text = df.iloc[j]['cleaned_discovery']
            similarity = fuzz.ratio(base_text, compare_text)
            # If similarity exceeds the threshold, consider them duplicates
            if similarity >= threshold:
                group_ids[j] = current_group
        current_group += 1
    
    # Add the computed group ID to the DataFrame
    df['group_id'] = group_ids

    # Function to aggregate group records
    def aggregate_group(sub_df: pd.DataFrame) -> pd.Series:
        """
        Aggregate records within a duplicate group.
        - For the discovery name, use the record with the shortest cleaned text (as a representative).
        - For other fields, take the union of values.
        """
        # Choose representative record (with the shortest cleaned discovery string)
        rep = sub_df.loc[sub_df['cleaned_discovery'].str.len().idxmin()]
        # Aggregate Year of Invention by taking the union and joining with semicolon
        years = ';'.join(sorted(set(sub_df['Year of Invention'].astype(str))))
        # Aggregate Name of Inventor
        inventors = ';'.join(sorted(set(sub_df['Name of Inventor'])))
        # Aggregate Nationality
        nationalities = ';'.join(sorted(set(sub_df['Nationality'])))
        return pd.Series({
            'Year of Invention': years,
            'Name of Inventor': inventors,
            'Name of Scientific Discovery': rep['Name of Scientific Discovery'],
            'Nationality': nationalities
        })
    
    # Group by the duplicate group and aggregate
    deduped_df = df.groupby('group_id').apply(aggregate_group).reset_index(drop=True)
    return deduped_df

# ----------------------------
# Main function to execute the data cleaning and deduplication
# ----------------------------
def main():
    # Read the CSV files into pandas DataFrames
    df1 = pd.read_csv('raw_data/clean_data/cleaned_data_1.csv')
    df2 = pd.read_csv('raw_data/clean_data/cleaned_data_2.csv')
    
    # Concatenate the two datasets
    combined_df = pd.concat([df1, df2], ignore_index=True)
    
    # Apply deduplication on the combined data with a chosen similarity threshold
    deduped_df = deduplicate_discoveries(combined_df, threshold=90)
    
    # Save the deduplicated data to a new CSV file
    deduped_df.to_csv('deduped_data.csv', index=False)
    print("Deduplication complete. Results saved to 'deduped_data.csv'.")

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
