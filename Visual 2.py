import pygame
import random
from sys import exit

# global pygame settings
WIDTH = 1200
HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (127, 127, 127)

#experiment variables
Num_Of_Trials_Each_Period = 1
fore_periods = [400, 600, 800, 1000, 1200]
random_ISI = list(range(-325, 326))
conditions = ['rhythmic', 'Arrhithmic']

#visuals
stim_color = BLUE
stim_size = 200

fixation_size = 7
fixation_color = WHITE
fixation_time = 1500
inter_trial_delay = 1500


#General Lists
randomized_ISI_list = []
foreperiods_list_rhythmic = []
foreperiods_list_Arrhythmic = []
foreperiods_pool = []
Center = [(200, 425), (250, 425), (250, 375), (200, 375)]



def Create_Foreperiod_Pool():
    for i in fore_periods:
        for j in range(Num_Of_Trials_Each_Period):
            foreperiods_pool.append(i)

def print_information():
    print('first condition =', start_condition)
    print('second condition =', conditions[0])
    print('the randomized ISI for Arrhythmic =', randomized_ISI_list)
    print('Arrhythmic foreperiods chronologically\n', foreperiods_list_Arrhythmic)
    print('rhythmic foreperiods chronologically\n', foreperiods_list_rhythmic)

class SimpleDecisionTask(object):
    def __init__(self):
        # screen parameters
        pygame.init()
        size = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.font = pygame.font.SysFont("Arial", 30)
        self.colors = {'Blue': BLUE, "Red": RED}

        # experiments parameters
        self.First_ISI = 800
        self.ISI = 700
        self.stimuli_duration = 100
        self.trial_num = 50
        self.instruction_msg = "Press Space Key To Start"
        self.instruction_msg2 = 'press ESC to Exit'


    def display_text_on_screen(self, text_str, text_str_2):
        text = self.font.render(text_str, True, WHITE)
        textrect = text.get_rect()
        textrect.centerx = self.screen.get_rect().centerx
        textrect.centery = self.screen.get_rect().centery
        self.screen.blit(text, textrect)
        text = self.font.render(text_str_2, True, WHITE)
        textrect = text.get_rect()
        textrect.centerx = self.screen.get_rect().centerx
        textrect.centery = self.screen.get_rect().centery+150
        self.screen.blit(text, textrect)
        pygame.display.flip()


    def start_instruction_screen(self):
        self.display_text_on_screen(self.instruction_msg, self.instruction_msg2)
        self.wait_for_press()
        # pygame.time.delay(self.between_trials_time)

    def stimuli_display(self, color=stim_color, size=stim_size):
        #Display the stimuli for period of time
        pygame.draw.circle(self.screen, color, (self.screen.get_rect().centerx, self.screen.get_rect().centery), size)
        pygame.display.flip()
        pygame.time.delay(self.stimuli_duration)
        self.screen.fill(BLACK)
        pygame.display.flip()


    def Fixation_display(self, color = fixation_color, size=fixation_size):
        #Display the stimuli for period of time
        self.screen.fill(BLACK)
        pygame.display.flip()
        pygame.time.delay(inter_trial_delay)
        pygame.draw.circle(self.screen, color, (self.screen.get_rect().centerx, self.screen.get_rect().centery), size)
        pygame.display.flip()
        pygame.time.delay(fixation_time)
        self.screen.fill(BLACK)
        pygame.display.flip()

    def wait_for_press(self):
        pygame.event.clear()
        continue_flag = True
        while continue_flag:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        cur_key = "SPACE"
                        continue_flag = False
                    if event.key == pygame.K_ESCAPE:
                        cur_key = "ESC"
                        pygame.display.quit()
                        pygame.quit()
                        exit()
                        continue_flag = False
        pygame.event.clear()
        return cur_key


    def run_round_rhythmic(self):
#        cur_round = self.rounds[round_index]

        # present two options after short delay
        self.Fixation_display()

        # present target
        pygame.time.delay(self.First_ISI)
        self.stimuli_display()
        for i in range(3):
            pygame.time.delay(self.ISI)
            self.stimuli_display()
        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))
        foreperiods_list_rhythmic.append(foreperiod)
        pygame.time.delay(foreperiod)
        self.stimuli_display()
        self.trial_num -= 1

        pygame.event.clear()

    def run_round_Arrhythmic(self):

        # present two options after short delay
        self.Fixation_display()

        # present target
        pygame.time.delay(self.First_ISI)
        self.stimuli_display()
        for i in range(3):
            randomized_ISI = (700 + random_ISI.pop(random.randrange(len(random_ISI))))
            randomized_ISI_list.append(randomized_ISI)
            pygame.time.delay(randomized_ISI)
            self.stimuli_display()
        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))
        foreperiods_list_Arrhythmic.append(foreperiod)
        pygame.time.delay(foreperiod)
        self.stimuli_display()
        self.trial_num -= 1

        pygame.event.clear()

    # def get_results(self):
    #     """ save CSV file of the results stored in the round_scores attribute"""
    #     return pd.DataFrame(data=self.round_scores, columns=self.round_scores_titles)

    def run_condition(self, first_block):
        # start the rounds of the game
            if first_block == 'rhythmic':
                print('i was rhythmich this time')
                for trial in range(len(foreperiods_pool)):
                    self.run_round_rhythmic()
            else:
                for trial in range(len(foreperiods_pool)):
                    self.run_round_Arrhythmic()


Experiment = SimpleDecisionTask()
Experiment.start_instruction_screen()
Create_Foreperiod_Pool()
#First Block
start_condition = conditions.pop(random.randrange(len(conditions)))
Experiment.run_condition(start_condition)
pygame.time.delay(inter_trial_delay)
Experiment.display_text_on_screen(text_str= 'take a little break', text_str_2= 'to continue, Press SPACE key')
Experiment.wait_for_press()

#Second_Block
foreperiods_pool = []
Create_Foreperiod_Pool()
Experiment.run_condition(conditions[0])
pygame.time.delay(inter_trial_delay)
Experiment.display_text_on_screen(text_str='Thanks for the participation', text_str_2='To finish, Press SPACE key')
print_information()
Experiment.wait_for_press()
pygame.display.quit()
pygame.quit()
exit()
