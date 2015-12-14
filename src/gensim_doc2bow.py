import logging, sys, pprint

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

### Generating a training/background corpus from your own source of documents
from gensim.corpora import TextCorpus, MmCorpus, Dictionary

# gensim docs: "Provide a filename or a file-like object as input and TextCorpus will be initialized with a
# dictionary in `self.dictionary`and will support the `iter` corpus method. For other kinds of corpora, you only
# need to override `get_texts` and provide your own implementation."
background_corpus = TextCorpus(input=YOUR_CORPUS)

# Important -- save the dictionary generated by the corpus, or future operations will not be able to map results
# back to original words.
background_corpus.dictionary.save(
    "my_dict.dict")

MmCorpus.serialize("background_corpus.mm",
    background_corpus)  #  Uses numpy to persist wiki corpus in Matrix Market format. File will be several GBs.

### Generating a large training/background corpus using Wikipedia
from gensim.corpora import WikiCorpus, wikicorpus

articles = "enwiki-latest-pages-articles.xml.bz2"  # available from http://en.wikipedia.org/wiki/Wikipedia:Database_download

# This will take many hours! Output is Wikipedia in bucket-of-words (BOW) sparse matrix.
wiki_corpus = WikiCorpus(articles)
wiki_corpus.dictionary.save("wiki_dict.dict")

MmCorpus.serialize("wiki_corpus.mm", wiki_corpus)  #  File will be several GBs.

### Working with persisted corpus and dictionary
bow_corpus = MmCorpus("wiki_corpus.mm")  # Revive a corpus

dictionary = Dictionary.load("wiki_dict.dict")  # Load a dictionary

### Transformations among vector spaces
from gensim.models import LsiModel, LogEntropyModel

logent_transformation = LogEntropyModel(wiki_corpus,
    id2word=dictionary)  # Log Entropy weights frequencies of all document features in the corpus

tokenize_func = wikicorpus.tokenize  # The tokenizer used to create the Wikipedia corpus
document = "Some text to be transformed."
# First, tokenize document using the same tokenization as was used on the background corpus, and then convert it to
# BOW representation using the dictionary created when generating the background corpus.
bow_document = dictionary.doc2bow(tokenize_func(
    document))
# converts a single document to log entropy representation. document must be in the same vector space as corpus.
logent_document = logent_transformation[[
    bow_document]]

# Transform arbitrary documents by getting them into the same BOW vector space created by your training corpus
documents = ["Some iterable", "containing multiple", "documents", "..."]
bow_documents = (dictionary.doc2bow(
    tokenize_func(document)) for document in documents)  # use a generator expression because...
logent_documents = logent_transformation[
                   bow_documents]  # ...transformation is done during iteration of documents using generators, so this uses constant memory

### Chained transformations
# This builds a new corpus from iterating over documents of bow_corpus as transformed to log entropy representation.
# Will also take many hours if bow_corpus is the Wikipedia corpus created above.
logent_corpus = MmCorpus(corpus=logent_transformation[bow_corpus])

# Creates LSI transformation model from log entropy corpus representation. Takes several hours with Wikipedia corpus.
lsi_transformation = LsiModel(corpus=logent_corpus, id2word=dictionary,
    num_features=400)

# Alternative way of performing same operation as above, but with implicit chaining
# lsi_transformation = LsiModel(corpus=logent_transformation[bow_corpus], id2word=dictionary,
#    num_features=400)

# Can persist transformation models, too.
logent_transformation.save("logent.model")
lsi_transformation.save("lsi.model")

### Similarities (the best part)
from gensim.similarities import Similarity

# This index corpus consists of what you want to compare future queries against
index_documents = ["A bear walked in the dark forest.",
             "Tall trees have many more leaves than short bushes.",
             "A starship may someday travel across vast reaches of space to other stars.",
             "Difference is the concept of how two or more entities are not the same."]
# A corpus can be anything, as long as iterating over it produces a representation of the corpus documents as vectors.
corpus = (dictionary.doc2bow(tokenize_func(document)) for document in index_documents)

index = Similarity(corpus=lsi_transformation[logent_transformation[corpus]], num_features=400, output_prefix="shard")

print "Index corpus:"
pprint.pprint(documents)

print "Similarities of index corpus documents to one another:"
pprint.pprint([s for s in index])

query = "In the face of ambiguity, refuse the temptation to guess."
sims_to_query = index[lsi_transformation[logent_transformation[dictionary.doc2bow(tokenize_func(query))]]]
print "Similarities of index corpus documents to '%s'" % query
pprint.pprint(sims_to_query)

best_score = max(sims_to_query)
index = sims_to_query.tolist().index(best_score)
most_similar_doc = documents[index]
print "The document most similar to the query is '%s' with a score of %.2f." % (most_similar_doc, best_score)