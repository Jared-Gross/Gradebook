import math
import random

messages = {
    0: [
        "It's just the beginning. Every master was once a disaster. Keep trying!",
        "Learning is a journey. Let's tackle the basics again together.",
        "Rome wasn't built in a day. Review the material and give it another shot!",
        "Mistakes are stepping stones to success. You've got this!",
        "Don't be disheartened. Persistence is key to mastery.",
        "The only failure is not trying. Let's dive in once more!",
        "Keep your spirits up! The breakthrough you seek is just around the corner.",
        "Every expert was once a beginner. Ready for another round?",
        "The path to success is paved with attempts. Keep going!",
        "This score doesn't define your potential. Onward and upward!"
    ],
    1: [
        "You're on the board! Let's build on that first point.",
        "A good start! Review what tripped you up and try again.",
        "One down, many more to go. You're getting there!",
        "You've cracked the surface. Keep pushing to go deeper!",
        "That's a start! Every point is a step in the right direction.",
        "First points are just the beginning. Keep the momentum going!",
        "You've made the first dent. Now, let's aim higher!",
        "A point earned is a learning confirmed. Keep adding to your score!",
        "With one point scored, you're on your way. Let's increase that count!",
        "Every journey starts with a single step. Ready for the next one?"
    ],
    2: [
        "You're laying the foundation. Let's strengthen it with another try.",
        "Two points! You're uncovering the right path. Keep exploring.",
        "You've got the basics. Time to build on them for a higher score.",
        "A solid start. Review what's unclear and the progress will show.",
        "You're on your way. A bit more focus, and you'll see major improvements.",
        "Gathering steam! Let's use what you've learned to push further.",
        "Two steps forward! Now, let's aim for the next leap.",
        "You're getting the hang of it. Keep the learning going!",
        "A couple of victories already. Imagine what's next!",
        "You've started your climb. Keep the momentum up!"
    ],
    3: [
        "Three cheers for your effort! Now, let's aim for even more.",
        "You're making your way up. Every step takes you closer to the top.",
        "Tackling the challenges one by one. Keep it up!",
        "You've got a good grasp of some concepts. Time to expand your knowledge.",
        "A trio of points! Let's triple this success in your next attempt.",
        "You're showing promise. Let's unveil your full potential.",
        "Three marks of progress. You're on the right trajectory!",
        "A commendable effort. Let's review and improve further.",
        "Growth is evident. Let's nurture it into excellence.",
        "You're uncovering the puzzle. Keep connecting the pieces."
    ],
    4: [
        "Fourfold success! Now, let's strive for more.",
        "You're nearly halfway there. Push through to the other side!",
        "A solid base to build upon. Let's elevate your understanding.",
        "Four points in the bag. Your journey of learning continues.",
        "You're getting closer to the summit. Keep climbing!",
        "Great job! You're understanding more and more. Keep going!",
        "With every question, you grow stronger. Keep the streak going!",
        "Four steps forward. The peak is in sight. Onward!",
        "You're showing real progress. Let's fine-tune your skills.",
        "Building block by block. You're constructing your success."
    ],
    5: [
        "Halfway to perfection! Let's bridge the gap to the top.",
        "A balanced effort. Now, tip the scales in your favor with more review.",
        "You've reached the midpoint. Now, the sky's the limit!",
        "Five out of ten! A solid foundation. Time to build the structure.",
        "Halfway there! With a bit more push, you'll reach new heights.",
        "You're in the middle of the journey. Keep your eyes on the prize.",
        "A commendable halfway mark. Let's aim for full marks next time.",
        "You've got a good grip. Tighten it for the perfect score.",
        "Half of the battle is won. Now, for the victory lap.",
        "You're on the right track. Keep the momentum to cover the other half."
    ],
    6: [
        "More than halfway there! Your efforts are showing.",
        "Six points! You're moving past the basics into mastery.",
        "You've crossed the midpoint. Keep the pace to reach the end.",
        "A strong effort with room to grow. Aim higher!",
        "You're making headway. Let's polish up the rough edges for a perfect score.",
        "Six successes! Now, let's conquer the remaining challenges.",
        "You're on a positive trajectory. Keep aiming for the stars.",
        "Great progress! A few tweaks and you're there.",
        "The finish line is getting closer. Sprint towards it!",
        "You've gathered a lot of knowledge. Time to make it complete."
    ],
    7: [
        "Great work! You're doing really well, but there's room for improvement.",
        "You've got a solid understanding. A little more effort could get you to perfect!",
        "Well done! You're clearly grasping the concepts. Try to nail down the rest.",
        "You're on the right track! Review the areas that are giving you trouble.",
        "Nice job! You're above average, but strive for even better.",
        "Strong performance! With a bit more study, you can achieve perfection.",
        "You've done well to get this far! Push a little further to excel.",
        "Good grasp on the material! A bit more refinement and you're there.",
        "You're doing great! Just a few tweaks and you could be at the top.",
        "Impressive work! Fine-tune your understanding to reach the peak."
    ],
    8: [
        "Very good! You're close to mastery, just a few more steps.",
        "Excellent effort! You're almost at the finish line, keep going.",
        "You've done extremely well! Let's iron out those last few kinks.",
        "So close to perfect! Review your work to find where you can improve.",
        "You're nearly there! A bit more practice and you'll have it.",
        "Fantastic work! Just a couple more points to perfection.",
        "You've shown great understanding! A little more effort for a full score.",
        "Almost flawless! Identify and work on the small gaps remaining.",
        "Superb! With a slight push, you can achieve the highest score.",
        "You're doing wonderfully! A final review could lead to perfect results."
    ],
    9: [
        "So close to perfection! Can you make it flawless?",
        "Excellent work! Just one more step to the summit.",
        "You've nearly mastered this. Aim for that perfect score!",
        "Outstanding achievement! Let's make it even better.",
        "Just a hair away from 100%! Review and perfect your knowledge.",
        "Amazing job! Let's polish it to a perfect 10.",
        "You're at the doorstep of mastery. Cross the threshold!",
        "A 9 is fantastic, but a 10? Now that's excellence.",
        "You've shown great skill. Now, aim for perfection.",
        "Brilliant performance! The final push can take you to perfection."
    ],
    10: [
        "Perfection! You've mastered this topic brilliantly.",
        "Incredible! You've achieved the highest standard of excellence.",
        "Flawless victory! Your hard work has truly paid off.",
        "A perfect score! You're an inspiration.",
        "Congratulations on a perfect result! Your dedication shines through.",
        "Remarkable achievement! You've set a high bar for excellence.",
        "Masterful performance! You've demonstrated complete understanding.",
        "Outstanding! A perfect score is a testament to your effort.",
        "Bravo! Perfection is not easy, but you've made it look so.",
        "Superb! You've reached the pinnacle of achievement in this challenge."
    ]
}


def random_message(score: float) -> str:
    return random.choice(messages[math.floor(score)])
