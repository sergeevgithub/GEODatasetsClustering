import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, HDBSCAN
from sklearn.preprocessing import normalize
import plotly.express as px
import plotly.io as pio

pio.renderers.default = "svg"

def fetch_geo_metadata(pmids):
    elink_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
    params = {
        "dbfrom": "pubmed",
        "db": "gds",
        "id": ','.join(pmids),
        "retmode": "json"
    }

    r = requests.get(elink_url, params=params).json()
    geo_ids = r['linksets'][0]['linksetdbs'][0]['links']
    print(f'Fetched {len(geo_ids)} links')

    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params2 = {
        "db": "gds",
        "id": ','.join(geo_ids),
        "retmode": "json"
    }

    r = requests.get(esummary_url, params=params2).json()

    data = []
    for geo_id in geo_ids:
        geo_info = r['result'][geo_id]
        gse_id = 'GSE' + geo_info['gse']
        title = geo_info['title']
        experiment_type = geo_info['gdstype']
        summary = geo_info['summary']
        organism = geo_info['taxon']

        link = f'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse_id}'
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            overall_design = 'Overall design: ' + '; '.join(
                soup.find("td", string="Overall design").find_next_sibling("td").stripped_strings)
        else:
            print(f"Failed to retrieve data from {link}")
            overall_design = 'Overall design: not fetched'

        contents = ' '.join([title, experiment_type, summary, organism, overall_design])

        relevant_pubmedids = [pubmedid for pubmedid in geo_info['pubmedids'] if pubmedid in pmids]
        data.append({
            'geo_id': geo_id,
            'gse_id': gse_id,
            'contents': contents,
            'pmids': relevant_pubmedids,
        })

    return pd.DataFrame(data)


def vectorize_and_cluster(df):
    print('Vectorizing...')
    vectorizer = TfidfVectorizer(
        lowercase=True,
        max_df=0.9,
        min_df=5,
        # ngram_range=(1,3),
        stop_words='english',
    )
    tfidf_matrix = vectorizer.fit_transform(df['contents'])
    print('Clustering...')
    # KMeans
    tfidf_matrix_normalized = normalize(tfidf_matrix)
    df['kmeans_label'] = KMeans(n_clusters=2, init='k-means++', random_state=42, n_init=10).fit_predict(tfidf_matrix_normalized)

    # HDBSCAN
    df['hdb_label'] = HDBSCAN(min_cluster_size=8, min_samples=3, metric='cosine').fit_predict(tfidf_matrix)

    pca_2d = PCA(n_components=2).fit_transform(tfidf_matrix)
    pca_3d = PCA(n_components=3).fit_transform(tfidf_matrix)
    df['x_2d'], df['y_2d'] = pca_2d[:, 0], pca_2d[:, 1]
    df['x_3d'], df['y_3d'], df['z_3d'] = pca_3d[:, 0], pca_3d[:, 1], pca_3d[:, 2]

    return df


def get_plots(df):
    print('Plotting...')
    plot_dict = dict()

    plot_dict['plot_kmeans_2d'] = px.scatter(df, x='x_2d', y='y_2d', color=df['kmeans_label'].astype(str),
                                             hover_data=['pmids', 'gse_id']).to_html(full_html=False)
    plot_dict['plot_hdbscan_2d'] = px.scatter(df, x='x_2d', y='y_2d', color=df['hdb_label'].astype(str),
                                              hover_data=['pmids', 'gse_id']).to_html(full_html=False)
    plot_dict['plot_kmeans_3d'] = px.scatter_3d(df, x='x_3d', y='y_3d', z='z_3d', color=df['kmeans_label'].astype(str),
                                                hover_data=['pmids', 'gse_id']).to_html(full_html=False)
    plot_dict['plot_hdbscan_3d'] = px.scatter_3d(df, x='x_3d', y='y_3d', z='z_3d', color=df['hdb_label'].astype(str),
                                                 hover_data=['pmids', 'gse_id']).to_html(full_html=False)

    return plot_dict


def process_pmids(pmids):
    df = fetch_geo_metadata(pmids)
    plots = get_plots(vectorize_and_cluster(df))
    return plots
