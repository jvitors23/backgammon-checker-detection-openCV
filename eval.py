import os
import os.path as P
import fire
from loguru import logger
from glob import glob
import json
import numpy as np


PIPS_NUM = 24

def eval_sample(gt, pred_file):
    logger.info(P.basename(pred_file))
    with open(pred_file, 'r') as p:
        pred = json.load(p)

    gt_ar = np.uint8(gt['top'] + gt['bottom'])
    logger.info('gt_ar\n'+f'{gt_ar}')
    pred_ar = np.uint8(pred['top'] + pred['bottom'])
    logger.info('pred_ar\n'+f'{pred_ar}')

    matching_pips = np.sum(gt_ar == pred_ar)
    is_full_match = PIPS_NUM == matching_pips
    logger.info('matching_pips\n'+f'{matching_pips}')
    logger.info('is_full_match\n'+f'{is_full_match}')

    return matching_pips, is_full_match


@logger.catch
def eval_dir(pred_dir, gt_file, result_file='result.txt'):
    print(pred_dir)
    pred_fns = glob(P.join(pred_dir, '*.checkers.json'))
    with open(gt_file, 'r') as g:
        gts = json.load(g)

    total_pips = 0
    total_matching_pips = 0
    full_matches = 0
    boards = 0

    for pred in pred_fns:
        bn = P.basename(pred)
        gt = gts[bn]
        matching_pips, is_full_match = eval_sample(gt, pred)

        total_matching_pips += matching_pips
        total_pips += PIPS_NUM
        full_matches += int(is_full_match)
        boards += 1

    matching_pips_pct = f'{total_matching_pips*100/total_pips:6.2f}%'
    full_matches_pct = f'{full_matches*100/boards:6.2f}%'

    if P.isfile(result_file):
        os.remove(result_file)
    logger.add(result_file, format='{message}')

    logger.info(f'matching pips pct: {matching_pips_pct}')
    logger.info(f'full matches pct:  {full_matches_pct}')

if __name__ == "__main__":
    fire.Fire(eval_dir)