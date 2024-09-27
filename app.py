import logging
from cross_align.data_loader import load_fasttext_model, get_top_n_words, load_bilingual_lexicon
from cross_align.alignement import align_embeddings, apply_alignment
from cross_align.evaluation import word_translation_accuracy, analyze_cosine_similarities, ablation_study, plot_ablation_results
import numpy as np

# Set up logging: console and file
def setup_logging():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG,
                        format=log_format,
                        handlers=[
                            logging.FileHandler("logs/alignment.log"),   # Logs to a file
                            logging.StreamHandler()                # Logs to console
                        ])

def main():
    # Initialize logging
    setup_logging()
    
    logging.info("Starting cross-lingual alignment pipeline...")

    embedding_dir = "./embeddings/pretrained/"
    muse_dir = "lexicon/"

    # Load FastText models and vocabularies
    logging.info("Loading FastText models...")
    en_embeddings = load_fasttext_model(embedding_dir, 'en')
    hi_embeddings = load_fasttext_model(embedding_dir, 'hi')

    en_words = get_top_n_words(en_embeddings)
    hi_words = get_top_n_words(hi_embeddings)

    logging.info("Loading bilingual lexicon...")
    train_dict = load_bilingual_lexicon(muse_dir, 'en', 'hi')
    test_dict = load_bilingual_lexicon(muse_dir, 'en', 'hi', train=False)

    # Supervised alignment (Procrustes)
    logging.info("Performing supervised alignment...")
    alignment_matrix = align_embeddings(en_embeddings, hi_embeddings, en_words, hi_words, train_dict)

    # Apply alignment to English model
    en_aligned_supervised = apply_alignment(en_embeddings, alignment_matrix)

    # Evaluate supervised alignment
    logging.info("Evaluating supervised alignment...")
    p1, p5 = word_translation_accuracy(en_aligned_supervised, hi_embeddings, en_words, hi_words, test_dict)
    logging.info(f"Supervised Alignment Results: Precision@1: {p1:.4f}, Precision@5: {p5:.4f}")

    # Analyze cosine similarities
    word_pairs = [('dog', 'कुत्ता'), ('cat', 'बिल्ली'), ('house', 'घर')]
    similarities = analyze_cosine_similarities(en_aligned_supervised, hi_embeddings, en_words, hi_words, word_pairs)
    logging.info("Cosine Similarities:")
    for src, tgt, sim in similarities:
        logging.info(f"{src} - {tgt}: {sim:.4f}")

    # Ablation study
    sizes = [5000, 10000, 20000]
    logging.info("Starting ablation study with sizes: 5000, 10000, 20000")
    ablation_results = ablation_study(en_embeddings, hi_embeddings, en_words, hi_words, train_dict, test_dict, sizes)
    
    # Plot ablation results
    plot_ablation_results(ablation_results)
    logging.info("Ablation study completed and plotted.")

if __name__ == "__main__":
    main()
