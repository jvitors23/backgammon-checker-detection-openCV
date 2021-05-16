# Deeper systems test

## Results:
matching pips pct:  90.00%
full matches pct:   40.00%

1. How well do you expect this to work on other images?

I believe my strategy will work well with similar images. However when I was implementing, I noticed that the vertical image was the most chalenging, this is because the image was in a difficult perspective, so I believe I need to test this aproach with images in more variate perspectives. The way I'm counting the checker per pip also need to be improved.

2. What are possible fail cases of this approach and how would you address them?

This approach depends on  remove the perspective from the image, so maybe in other images the transformation I used isn't work well, so with more time I could search for other ways to do the transform better. This approach will not work in cases where the checker is badly positioned, one thing that could be done is to try to verify how a checker is aligning with others in the same pip, and based on it count the checker. 


3. How would you implement finding the colors of the checkers and distinguishing which player the checker belongs to?

I would look at the region near the center pixel of each checker and based on the pixel values I could differentiate which player the checker belongs to.