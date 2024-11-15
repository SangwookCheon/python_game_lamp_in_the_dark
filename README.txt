CS190 FINAL PROJECT - Dec 14, 2022
Sangwook Cheon
A Lamb in the Dark

RESOURCES USED (Documentation):
https://api.arcade.academy/en/latest/tutorials/raycasting/index.html - light effect
https://api.arcade.academy/en/latest/tutorials/pymunk_platformer/index.html - physics engine

All artworks (walls, player, and enemies) are my own drawings.
Royalty-free Background music from Pixabay
Sound Effect from <a href="https://pixabay.com/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=music&amp;utm_content=18787">Pixabay</a>


HOW TO PLAY
Use direction keys to move the player, right and left, and 'up' key to jump.
Use 'z' to decrease the amount of light, and 'x' to make it brighter.

The map is consumed by complete darkness - you only have a small lamp to secure vision. Complete 5 levels as fast as
possible - can you beat the current best time?

You lose the game if the player falls into a hole or collides with a 'following' enemy. The enemy will follow when you
are nearby, but it cannot kill you if the light is reduced to zero. It can only kill with the presence of light - the
brighter it is, the faster it moves.

If the light is too bright (above the threshold), then the ground will be unstable and shake - you will no longer be able
to jump! Also, little rocks will fall on top of you. These cannot kill you - they may hinder or help you navigate the map.

You complete a level when you get to the right side of the screen. My game follows Bennett Foddy's principle of frustration -
if you die once, you start all over again... You can press Enter at any time to reset the game.

As the level increases, there are more holes and enemies. The map also becomes more complicated, making it difficult to
navigate without good skills and memory.


DESIGN CHOICES
- The core of this game is limiting visibility in a platformer game. By designing the maps in black, I maximized the
element of discovering parts of the world using only the light, while emphasizing that the world is consumed by darkness.
- The shadow effect is an entirely new mechanic --> the player must pay attention to curvature of light to identify any
holes, obstacles, etc. Playtesters noted this is intriguing.
-  I made sure that different parts of the world are visible with a reasonable amount of light, so that the player is able
to find clues for where to go next. If there is nothing nearby the player may feel hopeless.
- In some places, however, I designed holes so that the player needs to take an uncertain leap of faith.
- The 'following' enemy is sharp and slim, like an assassin - when it is spotted, the player will feel a sense of danger.
Personally, my heart dropped when I found an enemy right next to me after jumping.
- Including an eerie background music also added to the overall atmosphere of the game.

MEETING THE COMPLEXITY AND DISTINCTIVENESS REQUIREMENT
- I think a platformer game played in darkness is a unique concept! With shadow effect added, I created a different
gameplay experience where memory and securing visibility are most important.
To go beyond a simple platformer game, I designed multiple moving elements in the game, all managed under the same class
'Enemy.' Their movements are dynamic (depends on light radius, position of the player, and physics).
- Also, I made this game scalable - anyone can create a new level by making a folder with images of the world, a text file
listing enemies, and can even choose to draw text on the background (with a cool effect where it is revealed with light).
- I created effects like shaking the ground, and smooth switching between levels.

WHAT I LEARNED
- I learned the importance of prioritizing foundations of a game over finer components. I realized in the latter stages of
development that the design choices that I make now will probably need to be adjusted as more features are added and refined.
It was most efficient to make the game 'work' as I intended, instead of 'look' as I intended.
- I learned that making a piece of software that is flexible and adaptable is best in the long-run. Because I designed my game
so that levels can be added without writing any new piece of code, I was able to test levels more efficiently and helped
me easily identify bugs.
What's more, because I had a solid foundation, it was super easy to go back to the code and add a new feature,
while keeping the scalability.
- I learned that games do contain so much of what's going on inside the designer's mind - the design choices, how mechanics are
created, what dynamics are intended, etc.



