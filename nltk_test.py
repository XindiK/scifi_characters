import nltk
import sys
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim import corpora
from gensim.models import LdaModel

# Download NLTK data files (run only once)
nltk.download('punkt')
nltk.download('stopwords')

# file_name from the command-line argument
file_name = sys.argv[1]

# Load File
file_path = f"{file_name}.txt"

with open(file_path, "r", encoding="utf-8") as file:
    dialogues = file.read()

# # Preprocess the text
# stop_words = set(stopwords.words("english"))

# Define custom stop words
custom_stop_words = {"caleb", "ava", "nathan", "beat"}  # Add your custom stop words here

# Update the NLTK stop words set
stop_words = set(stopwords.words("english")).union(custom_stop_words)

def preprocess_text(text):
    # Tokenize into sentences, then words
    sentences = sent_tokenize(text)
    tokenized_sentences = [word_tokenize(sentence.lower()) for sentence in sentences]
    # Remove stop words and non-alphabetic tokens
    filtered_sentences = [
        [word for word in sentence if word.isalpha() and word not in stop_words]
        for sentence in tokenized_sentences
    ]
    return filtered_sentences

# Preprocess File
tokenized_data = preprocess_text(dialogues)

# Create a dictionary and corpus for LDA
dictionary = corpora.Dictionary(tokenized_data)
corpus = [dictionary.doc2bow(sentence) for sentence in tokenized_data]

# Train an LDA model
num_topics = 10  # You can adjust the number of topics
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, random_state=42, passes=10)

# Print the topics
print("\nLDA Topics:")
for idx, topic in lda_model.print_topics(num_words=5):
    print(f"Topic {idx}: {topic}")