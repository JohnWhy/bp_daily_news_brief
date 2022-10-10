from bs4 import BeautifulSoup
import requests


def parse_articles(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    stories = soup.find_all(class_="news-wire-story-block")
    all_stories = {}
    for story in stories:
        try:
            try:
                region = story.find_all('a', class_='article-category')[1].get('title')
                if region not in all_stories.keys():
                    all_stories[region] = []
            except Exception as e:
                print(e)
                region = 'Unspecified'
                if region not in all_stories.keys():
                    all_stories[region] = []
            text = story.find_all('p', class_='has-text-align-left')[1].getText()
            authors = story.find_all('p', class_="has-text-align-left text-brand-gunsmoke-grey")[0].getText()
            article_link = story.find('h6').find('a').get('href')
            all_stories[region].append({'link': article_link, 'text': text,
                                        'authors': authors})
        except Exception as e:
            print(e)
            print('failed to parse')
            pass
    return all_stories
