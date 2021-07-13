import pygame
import random
from sys import exit
import pandas as pd
import tkinter as tk
from tkinter import simpledialog
import datetime
import pylsl
import os
import time
import multiprocessing
import nidaqmx
from GUI2 import App, name, number

#LSL configuration
LabRecorder_path = "C:\Program Files\JetBrains\PyCharm Community Edition 2020.1.1\LabStreamingLayer\LabRecorder\LabRecorder.exe"
EEG_module_path = "C:\Program Files\JetBrains\PyCharm Community Edition 2020.1.1\LabStreamingLayer\labstreaminglayer\Apps\g.Tec\g.USBamp\gUSBamp.exe"
impedence_path = "C:\Program Files\JetBrains\PyCharm Community Edition 2020.1.1\LabStreamingLayer\labstreaminglayer\Apps\g.Tec\g.USBamp\gUSBamp.exe"

# global pygame settings
csv_output_path = r"C:\Users\fire-\OneDrive - rus10\#LIFE\Landau Lab\Lorenzo Project\The Press Mode\CSV\\"
#    r"C:\Users\fire-\PycharmProjects\The Press Mode Project\CSV_files\\"

WIDTH = 1200
HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREY = (167   , 167, 167)
LIGHT_BLUE = (0, 255, 255)
trial_info = []
time_stamps_start = []
time_stamps_end = []
time_stamps_first_stimuli = []


#experiment variables
Num_Of_Trials_Each_Period = 3
fore_periods = [600, 800, 1000]
conditions = ['single_m','single_d','entrainment_m','entrainment_d']                 #add arrhythmic here if needed

ISI = 800                     #first ISI
stimuli_duration = 100
target_duration = 100
disc_response_delay = 1500
response_window = 1500
random_ISI = list(range(-325, 326))

Num_Of_Catch_Trials = 1         #number of catch trials per block
catch_trial_delay = 1700        #time until the end of the trial in catch trials


#visuals
stim_color = GREY
stim_circle_size = 50
stim_square_size = stim_circle_size * 2
stim_triangle_size = stim_circle_size * 2

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


def create_csv(info, start_times, end_times, onset_times, name, number):
    output_CSV = pd.DataFrame(data=info, columns=['Num', 'Condition', 'Catch',
                                                           'ISI', 'Foreperiod'])
    output_CSV['Trial Start'] = start_times
    output_CSV['1st Simuli Onset'] = onset_times
    output_CSV['Trial End'] = end_times
    output_CSV.to_csv(output_path + number + '_' + name + '.csv', index=False)



class SimpleDecisionTask(object):
    '''
    THE EXPERIMENT CLASS
    '''
    def __init__(self):
        # screen parameters
        pygame.init()
        self.trigg_outlet = ''
        size = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.font = pygame.font.SysFont("Arial", 30)
        self.colors = {'Blue': BLUE, "Red": RED}
        self.trial_info = []
        self.trial_count = 1
        self.total_trial_num = 0
        self.current_stimuli_number = 1
        self.start_time = 0
        self.cur_key = ''
        self.target_choices = ['square', 'triangle']
        self.square_or_triangle_target_stimulus = self.target_choices.pop(random.randrange(len(self.target_choices)))
        self.square_or_triangle_non_target_stimulus = self.target_choices[0]

        # experiments parameters
        self.practice_length = 5
        self.First_ISI = ISI
        self.ISI = ISI - stimuli_duration
        self.disc_response_delay = disc_response_delay
        self.target_duration = target_duration
        self.stimuli_duration = stimuli_duration
        self.response_window = response_window
        self.constant_trials_per_condition = Num_Of_Trials_Each_Period + Num_Of_Catch_Trials
        self.trials_per_condition = Num_Of_Trials_Each_Period + Num_Of_Catch_Trials
        self.instruction_msg = "Press Space Key To Start"
        self.instruction_msg2 = 'press ESC to Exit at any time'

        self.CSV_df = pd.DataFrame(columns=['trial_start',	'practice',	'condition',	'press\passive',
                                            'ISI1',	'ISI2', 'ISI3', 'ISI4', 'catch', 'fix_end', '1_start_time',	'1_end_time',
                                        	'2_start_time',	'2_end_time',
                                            '3_start_time',	'3_end_time', 'foreperiod',	'target_start_time',
                                            'target_end_time',	'trial_end', 'target_type','response', 'target_stimulus'])


    def time_stamp(self):
        curr_time_stamp = datetime.datetime.now() - self.start_time
        return curr_time_stamp.total_seconds()


    def display_text_on_screen(self, text_str, text_str_2, text_str_3 = '', text_str_4=''):
        self.screen.fill(BLACK)
        pygame.display.flip()
        text = self.font.render(text_str, True, WHITE)
        textrect = text.get_rect()
        textrect.centerx = self.screen.get_rect().centerx
        textrect.centery = self.screen.get_rect().centery
        self.screen.blit(text, textrect)
        text = self.font.render(text_str_2, True, WHITE)
        textrect = text.get_rect()
        textrect.centerx = self.screen.get_rect().centerx
        textrect.centery = self.screen.get_rect().centery + 250
        self.screen.blit(text, textrect)
        text = self.font.render(text_str_3, True, WHITE)
        textrect = text.get_rect()
        textrect.centerx = self.screen.get_rect().centerx
        textrect.centery = self.screen.get_rect().centery + 45
        self.screen.blit(text, textrect)
        text = self.font.render(text_str_4, True, WHITE)
        textrect = text.get_rect()
        textrect.centerx = self.screen.get_rect().centerx
        textrect.centery = self.screen.get_rect().centery + 90
        self.screen.blit(text, textrect)
        pygame.display.flip()


    def Does_he_want_out(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.exit_screen()
                    quit()


    def start_instruction_screen(self):
        self.trigg_outlet.push_sample(['inst_start'])
        self.start_time = datetime.datetime.now()
        self.display_text_on_screen(self.instruction_msg, self.instruction_msg2)
        Experiment.wait_for_press()
        self.trigg_outlet.push_sample(['inst_end'])
        #pygame.time.delay(self.between_trials_time)



    def exit_screen(self):
        self.display_text_on_screen('to exit press ESCAPE', '')
        Experiment.wait_for_press()
        self.screen.fill(BLACK)
        pygame.display.flip()
        pygame.time.delay(1000)

    def stimuli_display(self, color=stim_color):
        #Display the stimuli for period of time
        self.CSV_df.loc[self.total_trial_num, str(self.current_stimuli_number) + '_start_time'] = self.time_stamp()
        pygame.draw.circle(self.screen, color, (self.screen.get_rect().centerx, self.screen.get_rect().centery), stim_circle_size)
        pygame.display.flip()
        self.trigg_outlet.push_sample(['circle_Show'])
        pygame.time.delay(self.stimuli_duration)
        self.screen.fill(BLACK)
        pygame.display.flip()
        self.trigg_outlet.push_sample(['circle_end'])
        self.CSV_df.loc[self.total_trial_num, str(self.current_stimuli_number) + '_end_time'] = self.time_stamp()

    def target_display(self, target_type = 'circle' ,color=stim_color):
        #Display the stimuli for period of time
         if target_type == 'circle':
            self.CSV_df.loc[self.total_trial_num, 'target_type'] = target_type
            self.CSV_df.loc[self.total_trial_num, 'target_start_time'] = self.time_stamp()
            pygame.draw.circle(self.screen, color, (self.screen.get_rect().centerx, self.screen.get_rect().centery), stim_circle_size)
            pygame.display.flip()
            self.trigg_outlet.push_sample(['target_cirlce_Show'])
            pygame.time.delay(self.target_duration)
            self.screen.fill(BLACK)
            pygame.display.flip()
            self.CSV_df.loc[self.total_trial_num, 'target_end_time'] = self.time_stamp()
            self.trigg_outlet.push_sample(['target_circle_end'])

         elif target_type == 'square':
            self.CSV_df.loc[self.total_trial_num, 'target_type'] = target_type
            self.CSV_df.loc[self.total_trial_num, 'target_start_time'] = self.time_stamp()
            pygame.draw.rect(self.screen, color, [self.screen.get_rect().centerx - (stim_square_size / 2),
                                                  self.screen.get_rect().centery - (stim_square_size / 2), stim_square_size, stim_square_size])
            pygame.display.flip()
            self.trigg_outlet.push_sample(['target_square_Show'])
            pygame.time.delay(self.target_duration+50)
            self.screen.fill(BLACK)
            pygame.display.flip()
            self.CSV_df.loc[self.total_trial_num, 'target_end_time'] = self.time_stamp()
            self.trigg_outlet.push_sample(['target_square_end'])

         elif target_type == 'triangle':
            self.CSV_df.loc[self.total_trial_num, 'target_type'] = target_type
            self.CSV_df.loc[self.total_trial_num, 'target_start_time'] = self.time_stamp()
            pygame.draw.polygon(self.screen, color, [(self.screen.get_rect().centerx, self.screen.get_rect().centery - stim_triangle_size / 2),
                                                     (self.screen.get_rect().centerx - stim_triangle_size / 2, self.screen.get_rect().centery + stim_triangle_size / 2),
                                                     ((self.screen.get_rect().centerx + stim_triangle_size /2, self.screen.get_rect().centery +  stim_triangle_size / 2))])
            pygame.display.flip()
            self.trigg_outlet.push_sample(['target_triangle_Show'])
            pygame.time.delay(self.target_duration)
            self.screen.fill(BLACK)
            pygame.display.flip()
            self.CSV_df.loc[self.total_trial_num, 'target_end_time'] = self.time_stamp()
            self.trigg_outlet.push_sample(['target_triangle_end'])




    def Fixation_display(self, color = fixation_color, size=fixation_size):
        self.Does_he_want_out() #checks if ESCAPE was pressed

        self.screen.fill(BLACK)
        pygame.display.flip()
        pygame.draw.circle(self.screen, color, (self.screen.get_rect().centerx, self.screen.get_rect().centery), size)
        pygame.display.flip()
        self.trigg_outlet.push_sample(['fix_start'])
        pygame.time.delay(fixation_time)
        self.screen.fill(BLACK)
        pygame.display.flip()
        self.trigg_outlet.push_sample(['fix_end'])
        self.CSV_df.loc[self.total_trial_num,'fix_end'] = self.time_stamp()

    def disc_press(self):
        pygame.event.clear()
        continue_flag = True
        while continue_flag:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    if event.key == pygame.K_3:
                        self.cur_key = "3"
                        continue_flag = False
                        pygame.event.clear()
                        self.trigg_outlet.push_sample(['Key_3'])

                    if event.key == pygame.K_4:
                        self.cur_key = "4"
                        continue_flag = False
                        pygame.event.clear()
                        self.trigg_outlet.push_sample(['Key_4'])
                        self.CSV_df.loc[self.total_trial_num, 'response'] = '4'


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
                        self.trigg_outlet.push_sample(['Key_space'])

                    if event.key == pygame.K_ESCAPE:
                        self.cur_key = "ESC"
                        pygame.display.quit()
                        pygame.quit()
                        exit()
                        continue_flag = False
                        pygame.event.clear()
        return self.cur_key

    def practice(self):
        # present target
        self.trigg_outlet.push_sample(['practice_inst_start'])
        self.display_text_on_screen(text_str='We will now start with a short practice.',
        text_str_2='to continue, Press SPACE key')
        pygame.time.delay(150)
        Experiment.wait_for_press()
        self.trigg_outlet.push_sample(['practice_inst_end'])

        for i in range(self.practice_length):
            self.current_stimuli_number = 1
            self.CSV_df.loc[self.total_trial_num, 'trial_start':'ISI4'] = [self.time_stamp(), 1, 'practice',
                                                                           'practice', self.ISI,
                                                                           self.ISI,
                                                                           self.ISI,
                                                                           self.ISI]
            self.trigg_outlet.push_sample(['practice_inst_end'])
            self.Fixation_display()
            self.CSV_df.loc[self.total_trial_num, 'fix_end'] = self.time_stamp()
            for i in range(3):
                self.Does_he_want_out()
                pygame.time.delay(self.ISI)
                self.stimuli_display()
                self.current_stimuli_number += 1
            foreperiod = random.randrange(400, 1200, 200)
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = foreperiod
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '0'
            pygame.time.delay(foreperiod)
            self.target_display('square')
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()
            pygame.time.delay(2000)
            pygame.event.clear()
            if self.total_trial_num < 2:
                self.display_text_on_screen(text_str='Press SPACE key',
                                            text_str_2='')
                Experiment.wait_for_press()
                pygame.event.clear()
                if self.total_trial_num == 1:
                    pygame.time.delay(100)
                    self.display_text_on_screen(text_str='We will continue the practice, without breaks',
                                                text_str_2='To continue, press SPACE')
                    Experiment.wait_for_press()
                    Experiment.wait_for_press()
                    pygame.event.clear()
            self.practice_length -= 1
            self.total_trial_num += 1
        self.display_text_on_screen(text_str='You will now start the experiment.',
                                    text_str_2='to continue, Press SPACE key')
        self.wait_for_press()
        Experiment.wait_for_press()


    ###### navigate_conditions ######
    def run_round_entrainment_d(self):
        pygame.time.delay(inter_trial_delay)
        self.total_trial_num += 1
        self.current_stimuli_number = 1
        self.CSV_df.loc[self.total_trial_num, 'trial_start':'ISI4'] = [self.time_stamp(), 0, 'entrainment',
                                                                            'disc', self.First_ISI, self.ISI, self.ISI,
                                                                                self.ISI]
        self.Fixation_display()
        self.Does_he_want_out() #checks if ESCAPE was pressed

        # present target
        pygame.time.delay(self.First_ISI)
        for i in range(3):
            self.stimuli_display()
            self.current_stimuli_number += 1
            self.Does_he_want_out()
            pygame.time.delay(self.ISI)
        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))
        shape = random.choice(['square','triangle'])

        if foreperiod != 1:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = foreperiod
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '0'
            pygame.time.delay(foreperiod)
            self.target_display(shape)
            self.CSV_df.loc[self.total_trial_num, 'target_type'] = [shape]
            self.trials_per_condition -= 1
            pygame.event.clear()
            pygame.time.delay(self.disc_response_delay)
            self.trigg_outlet.push_sample(['response_window_start'])
            self.display_text_on_screen(text_str='if you saw a '+self.square_or_triangle_target_stimulus+
                                        ' press harder now', text_str_2= '')
            pygame.time.delay(self.response_window)
            self.trigg_outlet.push_sample(['response_window_end'])
            self.screen.fill(BLACK)
            pygame.display.flip()
            pygame.time.delay(200)
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()

        else:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = 0
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '1'
            pygame.time.delay(catch_trial_delay)
            self.trials_per_condition -= 1
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()
            pygame.time.delay(inter_trial_delay)

    def run_round_entrainment_m(self):
        self.total_trial_num += 1
        self.current_stimuli_number = 1
        self.CSV_df.loc[self.total_trial_num, 'trial_start':'ISI4'] = [self.time_stamp(), 0, 'entrainment',
                                                                       'motor', self.First_ISI, self.ISI,
                                                                       self.ISI,
                                                                       self.ISI]
        self.Fixation_display()
        self.Does_he_want_out()  # checks if ESCAPE was pressed

        # present target
        pygame.time.delay(self.First_ISI)
        for i in range(3):
            self.stimuli_display()
            self.current_stimuli_number += 1
            self.Does_he_want_out()
            pygame.time.delay(self.ISI)
        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))
        shape = random.choice(['square', 'triangle'])

        if foreperiod != 1:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = foreperiod
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '0'
            pygame.time.delay(foreperiod)
            self.target_display(shape)
            self.trigg_outlet.push_sample(['response_window_start'])
            self.CSV_df.loc[self.total_trial_num, 'target_type'] = [shape]
            self.trials_per_condition -= 1
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()
            pygame.time.delay(inter_trial_delay)
            self.trigg_outlet.push_sample(['response_window_end'])

        else:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = 0
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '1'
            pygame.time.delay(catch_trial_delay)
            self.trials_per_condition -= 1
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()
            pygame.time.delay(inter_trial_delay)


    def run_round_single_d(self):
        pygame.time.delay(inter_trial_delay)
        self.total_trial_num += 1
        self.current_stimuli_number = 1
        self.CSV_df.loc[self.total_trial_num, 'trial_start':'ISI4'] = [self.time_stamp(), 0, 'single',
                                                                       'disc', self.First_ISI, '',
                                                                       '',
                                                                       '']
        self.Fixation_display()
        self.Does_he_want_out()  # checks if ESCAPE was pressed

        # present target
        pygame.time.delay(self.First_ISI)
        self.stimuli_display()
        pygame.time.delay(self.stimuli_duration)
        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))
        shape = random.choice(['square', 'triangle'])

        if foreperiod != 1:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = foreperiod
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '0'
            pygame.time.delay(foreperiod)
            self.target_display(shape)
            self.CSV_df.loc[self.total_trial_num, 'target_type'] = [shape]
            self.trials_per_condition -= 1
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()
            pygame.time.delay(self.disc_response_delay)
            self.trigg_outlet.push_sample(['response_window_start'])
            self.display_text_on_screen(text_str='if you saw a ' +self.square_or_triangle_target_stimulus+
                                                  ' press harder', text_str_2='')
            pygame.time.delay(self.response_window)
            self.trigg_outlet.push_sample(['response_window_end'])
            self.screen.fill(BLACK)
            pygame.display.flip()
            pygame.time.delay(200)
            pygame.event.clear()

        else:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = 0
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '1'
            pygame.time.delay(catch_trial_delay)
            self.trials_per_condition -= 1
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()

    def run_round_single_m(self):
        pygame.time.delay(inter_trial_delay)
        self.total_trial_num += 1
        self.current_stimuli_number = 1
        self.CSV_df.loc[self.total_trial_num, 'trial_start':'ISI4'] = [self.time_stamp(), 0, 'single',
                                                                       'motor', self.First_ISI, '',
                                                                       '',
                                                                       '']
        self.Fixation_display()
        self.Does_he_want_out()  # checks if ESCAPE was pressed

        # present target
        pygame.time.delay(self.First_ISI)
        self.stimuli_display()
        pygame.time.delay(self.stimuli_duration)
        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))
        shape = random.choice(['square', 'triangle'])

        if foreperiod != 1:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = foreperiod
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '0'
            pygame.time.delay(foreperiod)
            self.target_display(shape)
            self.trigg_outlet.push_sample(['response_window_start'])
            self.CSV_df.loc[self.total_trial_num, 'target_type'] = [shape]
            self.trials_per_condition -= 1
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()
            pygame.time.delay(inter_trial_delay)
            self.trigg_outlet.push_sample(['response_window_end'])

        else:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = 0
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '1'
            pygame.time.delay(catch_trial_delay)
            self.trials_per_condition -= 1
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()

    def run_round_Arrhythmic(self):
        self.total_trial_num += 1
        self.current_stimuli_number = 1
        self.CSV_df.loc[self.total_trial_num,'trial_start':'press\passive'] = [self.time_stamp(), 0 ,'arrhythmic', 'press/passive']
        # present two options after short delay
        self.Fixation_display()
        self.CSV_df.loc[self.total_trial_num,'fix_end'] = self.time_stamp()

        self.Does_he_want_out() #checks if ESCAPE was pressed

        # present target
        pygame.time.delay(self.First_ISI)
        self.stimuli_display()
        self.CSV_df.loc[self.total_trial_num, 'ISI' + str(self.current_stimuli_number)] = self.First_ISI
        current_trial_randomized_ISI = []
        for i in range(3):
            self.current_stimuli_number += 1
            self.Does_he_want_out()
            randomized_ISI = (700 + random_ISI.pop(random.randrange(len(random_ISI))))
            self.CSV_df.loc[self.total_trial_num, 'ISI' + str(self.current_stimuli_number)] = randomized_ISI
            pygame.time.delay(randomized_ISI)
            self.stimuli_display()


        foreperiod = foreperiods_pool.pop(random.randrange(len(foreperiods_pool)))

        if foreperiod != 1:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = foreperiod
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '0'
            # foreperiods_list_Arrhythmic.append(foreperiod)
            pygame.time.delay(foreperiod)
            self.target_display()
            self.trials_per_condition -= 1
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()

        else:
            self.CSV_df.loc[self.total_trial_num, 'foreperiod'] = 0
            self.CSV_df.loc[self.total_trial_num, 'catch'] = '1'
            pygame.time.delay(catch_trial_delay)
            self.trials_per_condition -= 1
            pygame.event.clear()
            self.CSV_df.loc[self.total_trial_num, 'trial_end'] = self.time_stamp()

    ####navigate run all conditions####
    def run_condition(self, curr_condition):
        # start the rounds of the game
        self.trials_per_condition = self.constant_trials_per_condition
        if curr_condition == 'single_m':
            self.display_text_on_screen(text_str='You will see a single circle followed by a square or a triangle.',
                                        text_str_2='Press SPACE to continue',
                                        text_str_3='if you see a ' +self.square_or_triangle_target_stimulus +
                                        ' press harder.')
            pygame.time.delay(150)
            self.wait_for_press()
            self.screen.fill(BLACK)
            pygame.display.flip()
            pygame.time.delay(200)
            pygame.event.clear()
            count = 0
            block_length = len(foreperiods_pool)            # counting trials for breaks
            for trial in range(len(foreperiods_pool)):     # taking a break at half the block
                if count == (int(round(block_length/2))):
                    pygame.time.delay(1000)
                    self.trigg_outlet.push_sample(['break_start'])
                    Experiment.display_text_on_screen(text_str='take a little break',
                                                      text_str_2='to continue, Press SPACE key')
                    Experiment.wait_for_press()
                    self.trigg_outlet.push_sample(['break_end'])
                    self.screen.fill(BLACK)
                    pygame.display.flip()
                    pygame.time.delay(1500)

                self.run_round_single_m()
                self.total_trial_num += 1
                count += 1

        elif curr_condition == 'single_d':
            self.display_text_on_screen(text_str='You will now see one circle followed by a square or a triangle. afterwhich there will be a short delay.',
                                        text_str_2='Press SPACE to continue',
                                        text_str_3='after each trial, report if you saw a '+self.square_or_triangle_target_stimulus+ ' by pressing harder.',
                                        text_str_4='if you saw a '+self.square_or_triangle_non_target_stimulus+' maintain the same force.')
            pygame.time.delay(150)
            self.wait_for_press()
            self.screen.fill(BLACK)
            pygame.display.flip()
            pygame.time.delay(200)
            pygame.event.clear()
            count = 0
            block_length = len(foreperiods_pool)            # counting trials for breaks
            for trial in range(len(foreperiods_pool)):     # taking a break at half the block
                if count == (int(round(block_length/2))):
                    pygame.time.delay(1000)
                    self.trigg_outlet.push_sample(['break_start'])
                    Experiment.display_text_on_screen(text_str='take a little break',
                                                      text_str_2='to continue, Press SPACE key')
                    Experiment.wait_for_press()
                    self.trigg_outlet.push_sample(['break_end'])
                    self.screen.fill(BLACK)
                    pygame.display.flip()
                    pygame.time.delay(1500)

                self.run_round_single_d()
                self.total_trial_num += 1
                count += 1

        elif curr_condition == 'entrainment_m':
            self.display_text_on_screen(text_str='You will see a 3 circles followed by a square or a triangle.',
                                        text_str_2='Press SPACE to continue',
                                        text_str_3='if you see a ' + self.square_or_triangle_target_stimulus +
                                                   ' press harder.')
            pygame.time.delay(150)
            Experiment.wait_for_press()
            self.screen.fill(BLACK)
            pygame.display.flip()
            pygame.time.delay(200)
            pygame.event.clear()
            count = 0
            block_length = len(foreperiods_pool)            # counting trials for breaks
            for trial in range(len(foreperiods_pool)):     # taking a break at half the block
                if count == (int(round(block_length/2))):
                    pygame.time.delay(1000)
                    self.trigg_outlet.push_sample(['break_start'])
                    Experiment.display_text_on_screen(text_str='take a little break',
                                                      text_str_2='to continue, Press SPACE key')
                    Experiment.wait_for_press()
                    self.trigg_outlet.push_sample(['break_end'])
                    self.screen.fill(BLACK)
                    pygame.display.flip()
                    pygame.time.delay(1500)

                self.run_round_entrainment_m()
                self.total_trial_num += 1
                count += 1

        elif curr_condition == 'entrainment_d':
            self.display_text_on_screen(text_str='You will now see 3 circles followed by a square or a triangle. afterwhich there will be a short delay.',
                                        text_str_2='Press SPACE to continue',
                                        text_str_3='after each trial, report if you saw a '+self.square_or_triangle_target_stimulus+ ' by pressing harder.',
                                        text_str_4='if you saw a '+self.square_or_triangle_non_target_stimulus+' keep pressing with the same force.')
            pygame.time.delay(150)
            self.wait_for_press()
            self.screen.fill(BLACK)
            pygame.display.flip()
            pygame.time.delay(200)
            pygame.event.clear()
            count = 0
            block_length = len(foreperiods_pool)            # counting trials for breaks
            for trial in range(len(foreperiods_pool)):     # taking a break at half the block
                if count == (int(round(block_length/2))):
                    pygame.time.delay(1000)
                    self.trigg_outlet.push_sample(['break_start'])
                    Experiment.display_text_on_screen(text_str='take a little break',
                                                      text_str_2='to continue, Press SPACE key')
                    self.wait_for_press()
                    self.trigg_outlet.push_sample(['break_end'])
                    self.screen.fill(BLACK)
                    pygame.display.flip()
                    pygame.time.delay(1500)

                self.run_round_entrainment_d()
                self.total_trial_num += 1
                count += 1

        elif curr_condition == 'arrhythmic':
            count = 0
            block_length = len(foreperiods_pool)
            for trial in range((len(foreperiods_pool))):
                if count == (int(round(block_length / 2))):
                    self.trigg_outlet.push_sample(['break_start'])
                    Experiment.display_text_on_screen(text_str='take a little break',
                                                      text_str_2='to continue, Press SPACE key')
                    self.wait_for_press()
                    self.trigg_outlet.push_sample(['break_end'])
                    self.screen.fill(BLACK)
                    pygame.display.flip()
                    pygame.time.delay(1500)
                self.run_round_Arrhythmic()
                self.total_trial_num += 1
                count += 1






def start_experiment():
    #start experiment
    Experiment = SimpleDecisionTask()
    Experiment.start_instruction_screen()
    Create_Foreperiod_Pool()

    #First Block
    start_condition = conditions.pop(random.randrange(len(conditions)))
    Experiment.run_condition(start_condition)
    trigg_outlet.push_sample(['first_block_end'])
    pygame.time.delay(inter_trial_delay)
    Experiment.display_text_on_screen(text_str='you have reached 50%', text_str_2='to continue, Press SPACE key')
    Experiment.wait_for_press()
    trigg_outlet.push_sample(['second_block_start'])

    #Second_Block
    foreperiods_pool = []
    Create_Foreperiod_Pool()
    Experiment.run_condition(conditions[0])
    pygame.time.delay(inter_trial_delay)

    #End screen and create CSV
    Experiment.display_text_on_screen(text_str='Thanks for the participation', text_str_2='To finish, Press SPACE key')
    pygame.time.delay(1500)
    create_csv(trial_info, time_stamps_start, time_stamps_end, time_stamps_first_stimuli)   # app.name, app.num
    run_boy = False
    Experiment.wait_for_press()
    pygame.display.quit()
    pygame.quit()
    exit()



def Ni_data_collection():
    streams = pylsl.resolve_stream()
    info = pylsl.stream_info('Force', 'Data', 1, 1000, 'float32')
    outlet = pylsl.stream_outlet(info)

    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        while True:
            sample = pylsl.vectorf([task.read()])
            outlet.push_sample(sample)
            time.sleep(0.01)




Ni_collect_proccess = multiprocessing.Process(target=Ni_data_collection)
#experiment_proccess= multiprocessing.Process(target=start_experiment)

if __name__ == '__main__':
    trigg_info = pylsl.stream_info('Markers', 'Markers', 1, 0, 'string')
    trigg_outlet = pylsl.stream_outlet(trigg_info)
    app = App(LabRecorder_path, EEG_module_path, impedence_path, Ni_collect_proccess)
    app.root.mainloop()
    # message if EEG is not activated
    if app.EEG_var == 0:
        root2 = tk.Tk()
        root2.withdraw()
        result = tk.messagebox.askokcancel(title=None,
                                           message='No EEG Signal. \nWould you like to procceed?', )
        if result == False:
            quit()

    if app.Ni_var == 0:
        root2 = tk.Tk()
        root2.withdraw()
        result = tk.messagebox.askokcancel(title=None,
                                           message='No Ni Card Signal. \nWould you like to procceed?', )
        if result == False:
            quit()

    # message if LabRecorder not activated
    if app.LabRecorder_var == 0:
        root2 = tk.Tk()
        root2.withdraw()
        result = tk.messagebox.askokcancel(title=None, message='LabRecorder not active. \n Do you wish to procceed?', )
        if result == False:
            quit()


    Experiment = SimpleDecisionTask()
    Experiment.trigg_outlet = trigg_outlet
    pygame.mouse.set_visible(False)
    Experiment.start_instruction_screen()
    #Experiment.practice()
    cur_block = 0
    for i in range(len(conditions)):
        Create_Foreperiod_Pool()
        cur_block +=1
        cur_condition = conditions.pop(random.randrange(len(conditions)))
        trigg_outlet.push_sample(['block_start'])
        Experiment.run_condition(cur_condition)
        pygame.time.delay(inter_trial_delay)
        if  cur_block == 2:
            Experiment.display_text_on_screen(text_str= 'You have reached 50%', text_str_2= 'to continue, Press SPACE key')
            Experiment.wait_for_press()
        trigg_outlet.push_sample(['block_end'])

    #End screen and create CSV
    Experiment.display_text_on_screen(text_str='Thanks for the participation', text_str_2='To finish, Press SPACE key')
    run_boy = False
    Experiment.CSV_df['target_stimulus'] = Experiment.square_or_triangle_target_stimulus
    Experiment.wait_for_press()
    name, number = str(name[0]), str(number[0])
    Experiment.CSV_df.to_csv(csv_output_path + number + '_' + name + '.csv', index=False)
    pygame.display.quit()
    pygame.quit()
    exit()
    quit()
