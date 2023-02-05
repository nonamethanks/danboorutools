A set of tools to make admining danbooru and making bots & automated changes easier.

All scripts are under danboorutools/scripts. You're on your own, and if I catch you abusing these on Danbooru I'll ban you.


To run the environment, do `docker compose up -d` and then go into the container with `docker exec -it -u danboorutools -w /code danboorutools /bin/bash poetry shell`.


## Scripts

#### Nuke Votes:
```
poetry run nuke_votes {comments|posts|all} user_id1 user_id2
```


#### Replace from e-hentai (interactive, posts from the last month):
```
poetry run replace_ehentai_samples
```
