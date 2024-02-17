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


#### Automatically create artist tags for posts that lack them
```
poetry run create_artist_tags {tags to search}
```


#### Post potential sockpuppets to a discord channel via webhook
```
poetry run sockpuppet_discord_monitor {test|production}
```


#### Suggest promotable users
```
poetry run promotions
```
