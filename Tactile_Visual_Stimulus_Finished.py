import pygame
import random
from sys import exit
import pandas as pd
import tkinter as tk
from tkinter import simpledialog


# global pygame settings
output_path = r"C:\\Users\fire-\OneDrive - rus10\\"
WIDTH = 1200
HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (127, 127, 127)
LIGHT_BLUE = (0, 255, 255)
trial_info = []
time_stamps_start = []
time_stamps_end = []
time_stamps_first_stimuli = []


#experiment variables
Num_Of_Trials_Each_Period = 1
fore_periods = [400, 600, 800, 1000, 1200]
conditions = ['rhythmic', 'Arrhithmic']

ISI = 800                     #first ISI
stimuli_duration = 100
random_ISI = list(range(-325, 326))

Num_Of_Catch_Trials = 1         #number of catch trials per block
catch_trial_delay = 1700        #time until the end of the trial in catch trials


#visuals
stim_color = LIGHT_BLUE
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
    #Add Catch trials
    for i in range(Num_Of_Catch_Trials):
        foreperiods_pool.append(1)


def csv_name():
    '''
    open GUI window asking participant name
    :return: str, name of participant for CSV file name
    '''

    ROOT = tk.Tk()
    ROOT.eval('tk::PlaceWindow . center')
    ROOT.withdraw()
    # the input dialog
    subj_name = simpledialog.askstring(title="Tactile Experiment",
                                  prompt="Enter Subject Name:")
    return subj_name


def create_csv(info, start_times, end_times, onset_times, name):
    output_CSV = pd.DataFrame(data=info, columns=['Num', 'Condition', 'Catch',
                                                           'ISI', 'Foreperiod'])
    output_CSV['Trial Start'] = start_times
    output_CSV['1st Simuli Onset'] = onset_times
    output_CSV['Trial End'] = end_times
    output_CSV.to_csv(output_path + name + '.csv', index=False)




class SimpleDecisionTask(object):
    '''
    THE EXPERIMENT CLASS
    '''
    def __init__(self):
        # screen parameters
        pygame.init()
        size = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.font = pygame.font.SysFont("Arial", 30)
        self.colors = {'Blue': BLUE, "Red": RED}
        self.trial_info = []
        self.trial_count = 1

        # experiments parameters
        self.First_ISI = ISI
        self.ISI = ISI - stimuli_duration
        self.stimuli_duration = stimuli_duration
        self.trial_num = Num_Of_Trials_Each_Period + Num_Of_Catch_Trials
        self.instruction_msg = "Press Space Key To Start"
        self.instruction_msg2 = 'press ESC to Exit at any time'


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


    def Does_he_want_out(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.exit_screen()


    def start_instruction_screen(self):
        self.display_text_on_screen(self.instruction_msg, self.instruction_msg2)
        self.wait_for_press()
        #pygame.time.delay(self.between_trials_time)

    def exit_screen(self):
        self.display_text_on_screen('to exit press ESCAPE', '')
        self.wait_for_press()
        self.screen.fill(BLACK)
        pygame.display.flip()
        pygame.time.delay(1000)

    def stimuli_display(self, color=stim_color, size=stim_size):
        #Display the stimuli for period of time
        pygame.draw.circle(self.screen, color, (self.screen.get_rect().centerx, self.screen.get_rect().centery), size)
        pygame.display.flip()
        pygame.time.delay(self.stimuli_duration)
        self.screen.fill(BLACK)
        pygame.display.flip()



    def Fixation_display(self, color = fixation_color, size=fixation_size):
        self.Does_he_want_out() #checks if ESCAPE was pressed

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
                        pygame.event.clear()
                    if event.key == pygame.K_ESCAPE:
                        cur_key = "ESC"
                        pygame.display.quit()
                        pygame.quit()
                        exit()
                        continue_flag = False
                        pygame.event.clear()
        return cur_key


    def run_round_rhythmic(self):
        self.Fixation_display()
        self.Does_he_want_out() #checks if ESCAPE was pressed

        # present target
        pygame.time.delay(self.First_ISI)
        time_stamps_first_stimuli.append(pygame.time.get_ticks())
        self.stimuli_display()
        for i in range(3):
            self.Does_he_want_out()
            pygame.time.delay(self.ISI)
            self.stimuli_display()
        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))
        if foreperiod != 1:
            trial_info.append([self.trial_count, 'Rhythmic', 0, [700,700,700], foreperiod])
            foreperiods_list_rhythmic.append(foreperiod)
            pygame.time.delay(foreperiod)
            self.stimuli_display()
            self.trial_num -= 1
            pygame.event.clear()
        else:
            trial_info.append([self.trial_count, 'Rhythmic', 1, [700,700,700], foreperiod])
            pygame.time.delay(catch_trial_delay)
            self.trial_num -= 1
            pygame.event.clear()

    def run_round_Arrhythmic(self):

        # present two options after short delay
        self.Fixation_display()
        self.Does_he_want_out() #checks if ESCAPE was pressed

        # present target
        time_stamps_first_stimuli.append(pygame.time.get_ticks())
        pygame.time.delay(self.First_ISI)
        self.stimuli_display()
        current_trial_randomized_ISI = []
        for i in range(3):
            self.Does_he_want_out()
            randomized_ISI = (700 + random_ISI.pop(random.randrange(len(random_ISI))))
            current_trial_randomized_ISI.append(randomized_ISI)
            pygame.time.delay(randomized_ISI)
            self.stimuli_display()
        randomized_ISI_list.append(current_trial_randomized_ISI)

        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))

        if foreperiod != 1:
            trial_info.append([self.trial_count, 'Arrhythmic', 0, current_trial_randomized_ISI, foreperiod])
            foreperiods_list_Arrhythmic.append(foreperiod)
            pygame.time.delay(foreperiod)
            self.stimuli_display()
            self.trial_num -= 1
            pygame.event.clear()
        else:
            trial_info.append(
                [self.trial_count, 'Arrhythmic', 1, current_trial_randomized_ISI, foreperiod])
            pygame.time.delay(catch_trial_delay)
            self.trial_num -= 1
            pygame.event.clear()


    def run_condition(self, curr_condition):
        # start the rounds of the game
            if curr_condition == 'rhythmic':
                for trial in range(len(foreperiods_pool)):
                    time_stamps_start.append(pygame.time.get_ticks())
                    self.run_round_rhythmic()
                    time_stamps_end.append(pygame.time.get_ticks())
                    self.trial_count += 1
            else:
                for trial in range(len(foreperiods_pool)):
                    time_stamps_start.append(pygame.time.get_ticks())
                    self.run_round_Arrhythmic()
                    time_stamps_end.append(pygame.time.get_ticks())
                    self.trial_count += 1


#open GUI for participant name
subj_name = csv_name()

#start experiment
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

#End screen and create CSV
Experiment.display_text_on_screen(text_str='Thanks for the participation', text_str_2='To finish, Press SPACE key')
create_csv(trial_info, time_stamps_start, time_stamps_end, time_stamps_first_stimuli, subj_name)
run_boy = False
Experiment.wait_for_press()
pygame.display.quit()
pygame.quit()
exit()
