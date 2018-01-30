def scrape(query, n_tweets, lang='en'):
    """
    Scrapes Twitter using Tweepy. Returns a dataframe of the most recent tweets that could be found. Also pickles this dataframe as 'raw_tweets/{query}.p'.
    
    Parameters
    ----------
    query: str
        Twitter search query.
        
    n_tweets: int
        The number of tweets to scrape.
        
    lang: str
        The language of tweets to search for. Default is 'en'.
        
    Returns
    -------
    tweets: Pandas DataFrame
        DataFrame where rows are tweets and columns are: timestamp, user_id, user_name, user_loc, user_lang, user_n_follows, text, n_rt
    """
    import pandas as pd, tweepy as tp
    import time
    from tqdm import tqdm_notebook # progress bar
    import os
    
    auth = tp.OAuthHandler('wHg7ow24tSmLMR59IVZxWjvwI', 'z0BdVVSTqjYHLFb7TldKssRCOWo7VqvYDAbaKtQLtmx9Cp9Sr9')
    auth.set_access_token('1634605514-QSQa8EkY3gWQLdrP44zAKjinRPN99fpdcifOdw6', 'CIRdV9KyWV0PyyaUKfrTDxJyz6T24qjk6dIb0Cs9upjK0')
    api = tp.API(auth)
    
    searched_tweets = []
    last_id = -1
    pbar = tqdm_notebook(total=n_tweets)
    
    while pbar.n < n_tweets:
        try:
            new_tweets = api.search(q=query, count=1000, max_id=str(last_id - 1), lang=lang) # get tweets older than oldest tweet in last batch
            if not new_tweets:
                break
            for tweet in new_tweets:
                searched_tweets.append(dict(
                    timestamp = tweet.created_at,
                    user_id = tweet.user.id,
                    user_name = tweet.user.screen_name,
                    user_loc = tweet.user.location,
                    user_lang = tweet.user.lang,
                    user_n_follows = tweet.user.friends_count,
                    text = tweet.text,
                    n_rt = tweet.retweet_count
                ))
                last_id = tweet.id
                pbar.update()
                if pbar.n >= n_tweets:
                    pbar.close()
                    break
        except tp.TweepError as e: # we've hit the Twitter API rate limit, need to wait
            print('sleeping at', dt.datetime.now().strftime('%-H:%M'))
            time.sleep(15*60+30) # sleep 15 min 30 sec -- Twitter API's minimum wait time
    if not os.path.exists('raw_tweets'):
        os.makedirs('raw_tweets')
    pd.DataFrame(searched_tweets).to_pickle(f'raw_tweets/{query.replace(" ","_")}.p')
    pbar.close()
    return pd.DataFrame(searched_tweets)