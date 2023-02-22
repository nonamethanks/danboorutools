A set of tools to make admining danbooru and making bots & automated changes easier.

All scripts are under danboorutools/scripts.

To run the environment, do `docker compose up -d` and then go into the container with `docker exec -it -u danboorutools -w /code danboorutools /bin/bash poetry shell`.


## Scripts

#### Nuke Votes:
```
poetry run nuke_votes {comments|posts|all} user_id1 user_id2
```

#### Nuke tag edits
```
poetry run nuke_tag_edits user_id tag_they_added
```


#### Replace from e-hentai (interactive, posts from the last month):
```
poetry run replace_ehentai_samples
```


#### Port the paid_reward tag from danbooru to gelbooru
```
poetry run tag_paid_rewards_on_gelbooru {latest|all}
```
