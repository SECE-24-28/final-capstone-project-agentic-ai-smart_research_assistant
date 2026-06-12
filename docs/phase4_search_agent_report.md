# Phase 4: Search Agent Validation Report

## Architecture
The Search Service utilizes **OpenAlex** as the primary scholarly data source. It was chosen over CrossRef due to consistent abstract availability (via inverted indices) and richer metadata fields.
The `SearchAgent` seamlessly normalizes the API responses into the local DB `Paper` schema.

## Search Queries

### Topic: Machine Learning
- **Search Time:** 2.85s
- **Papers Retrieved:** 3
- **Metadata Completeness:** 2/3 with full Title/Abstract/Authors.

**Top Result Example:**
- **Title:** Scikit-learn: Machine Learning in Python
- **Authors:** Fabián Pedregosa, Gaël Varoquaux, Alexandre Gramfort, Vincent Michel, Bertrand Thirion, Olivier Grisel, Mathieu Blondel, Müller, Andreas, Nothman, Joel, Louppe, Gilles, Peter Prettenhofer, Ron J. Weiss, Vincent Dubourg, Jake Vanderplas, Alexandre Passos, David Cournapeau, Matthieu Brucher, Matthieu Perrot, Édouard Duchesnay
- **Year:** 2012
- **DOI:** https://doi.org/10.48550/arxiv.1201.0490
- **Abstract Snippet:** Scikit-learn is a Python module integrating a wide range of state-of-the-art machine learning algorithms for medium-scale supervised and unsupervised ...

### Topic: Federated Learning
- **Search Time:** 2.49s
- **Papers Retrieved:** 3
- **Metadata Completeness:** 3/3 with full Title/Abstract/Authors.

**Top Result Example:**
- **Title:** Advances and Open Problems in Federated Learning
- **Authors:** Peter Kairouz, H. Brendan McMahan
- **Year:** 2020
- **DOI:** https://doi.org/10.1561/2200000083
- **Abstract Snippet:** Federated learning (FL) is a machine learning setting where many clients (e.g., mobile devices or whole organizations) collaboratively train a model u...

### Topic: Edge AI
- **Search Time:** 1.47s
- **Papers Retrieved:** 3
- **Metadata Completeness:** 3/3 with full Title/Abstract/Authors.

**Top Result Example:**
- **Title:** In-Edge AI: Intelligentizing Mobile Edge Computing, Caching and Communication by Federated Learning
- **Authors:** Xiaofei Wang, Yiwen Han, Chenyang Wang, Qiyang Zhao, Xu Chen, Min Chen
- **Year:** 2019
- **DOI:** https://doi.org/10.1109/mnet.2019.1800286
- **Abstract Snippet:** Recently, along with the rapid development of mobile communication technology, edge computing theory and techniques have been attracting more and more...

### Topic: Cyber Security
- **Search Time:** 2.12s
- **Papers Retrieved:** 3
- **Metadata Completeness:** 3/3 with full Title/Abstract/Authors.

**Top Result Example:**
- **Title:** A Survey of Data Mining and Machine Learning Methods for Cyber Security Intrusion Detection
- **Authors:** Anna L. Buczak, Erhan Guven
- **Year:** 2015
- **DOI:** https://doi.org/10.1109/comst.2015.2494502
- **Abstract Snippet:** This survey paper describes a focused literature survey of machine learning (ML) and data mining (DM) methods for cyber analytics in support of intrus...

### Topic: Healthcare AI
- **Search Time:** 2.29s
- **Papers Retrieved:** 3
- **Metadata Completeness:** 3/3 with full Title/Abstract/Authors.

**Top Result Example:**
- **Title:** Ethical and regulatory challenges of AI technologies in healthcare: A narrative review
- **Authors:** Ciro Mennella, Umberto Maniscalco, Giuseppe De Pietro, Massimo Esposito
- **Year:** 2024
- **DOI:** https://doi.org/10.1016/j.heliyon.2024.e26297
- **Abstract Snippet:** Over the past decade, there has been a notable surge in AI-driven research, specifically geared toward enhancing crucial clinical processes and outcom...

## Limitations
- The API is rate-limited without an email or API key, so a polite pool User-Agent is necessary.
- Abstracts from OpenAlex are provided as inverted indices and must be actively reconstructed.

## Recommended Production Approach
OpenAlex is fully viable for production. We recommend fetching a default of 5-10 papers, presenting them to the user on the frontend, and allowing the user to select the specific paper to fully ingest into the LLM Vector Store.