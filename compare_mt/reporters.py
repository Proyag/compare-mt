import matplotlib
from matplotlib import pyplot as plt 
plt.rcParams['font.family'] = 'sans-serif'
import numpy as np
import os

css_style = """
html {
  font-family: sans-serif;
}

table, th, td {
  border: 1px solid black;
}

th, td {
  padding: 2px;
}

tr:hover {background-color: #f5f5f5;}

tr:nth-child(even) {background-color: #f2f2f2;}

th {
  background-color: #396AB1;
  color: white;
}

caption {
  font-size: 14pt;
  font-weight: bold;
}

table {
  border-collapse: collapse;
}
"""

javascript_style = """
function myFunction(elem) {
  var x = document.getElementById(elem);
  if (x.style.display === "none") {
    x.style.display = "block";
  } else {
    x.style.display = "none";
  }
}
"""

bar_colors = ["#7293CB", "#E1974C", "#84BA5B", "#D35E60", "#808585", "#9067A7", "#AB6857", "#CCC210"]

def make_bar_chart(datas,
                   output_directory, output_fig_file, output_fig_format='png',
                   errs=None, sysnames=None, title=None, xlabel=None, xticklabels=None, ylabel=None):
  fig, ax = plt.subplots() 
  ind = np.arange(len(datas[0]))
  width = 0.7/len(datas)
  bars = []
  for i, data in enumerate(datas):
    err = errs[i] if errs != None else None
    bars.append(ax.bar(ind+i*width, data, width, color=bar_colors[i], bottom=0, yerr=err))
  ax.set_xticks(ind + width / 2)
  # Set axis/title labels
  if title is not None:
    ax.set_title(title)
  if xlabel is not None:
    ax.set_xlabel(xlabel)
  if ylabel is not None:
    ax.set_ylabel(ylabel)
  if xticklabels is not None:
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(xticklabels)
  else:
    ax.xaxis.set_visible(False) 

  if sysnames is None:
    sysnames = [f'Sys{i+1}' for (i, x) in enumerate(datas)]
  ax.legend(bars, sysnames)
  ax.autoscale_view()

  if not os.path.exists(output_directory):
    os.makedirs(output_directory)
  out_file = os.path.join(output_directory, f'{output_fig_file}.{output_fig_format}')
  plt.savefig(out_file, format=output_fig_format, bbox_inches='tight')

def html_img_reference(fig_file, title):
  return (f'<img src="{fig_file}.png" alt="{title}"> <br/>' +
          f'<button onclick="showhide(\\"{fig_file}_latex\\")">Show/Hide LaTeX</button> <br/>' +
          f'<div id="{fig_file}_latex">Test</div>')

class Report: 
  # def __init__(self, iterable=(), **kwargs):
  #   # Initialize a report by a dictionary which contains all the statistics
  #   self.__dict__.update(iterable, **kwargs)
  
  def print(self): 
    raise NotImplementedError('print must be implemented in subclasses of Report')

  def plot(self, output_directory, output_fig_file, output_fig_type):
    raise NotImplementedError('plot must be implemented in subclasses of Report')

  def print_header(self, header):
    print(f'********************** {header} ************************')

  def generate_report(self, output_fig_file=None, output_fig_format=None, output_directory=None):
    self.print()

    if output_fig_file is not None:
      self.plot(output_directory, output_fig_file, output_fig_format)

class ScoreReport(Report):
  def __init__(self, scorer_name, score1, str1, score2, str2, 
               wins=None, sys1_stats=None, sys2_stats=None):
    self.scorer_name = scorer_name 
    self.score1 = score1
    self.str1 = str1 
    self.score2 = score2 
    self.str2 = str2 
    self.sys1_stats = sys1_stats 
    self.sys2_stats = sys2_stats 
    self.wins = wins
    self.output_fig_file = None

  def print(self):
    self.print_header('Aggregate Scores')
    print(f'{self.scorer_name}:')
    if self.str1 is not None:
      print(f' Sys1: {self.score1} ({self.str1})\n Sys2: {self.score2} ({self.str2})')
    else:
      print(f' Sys1: {self.score1}\n Sys2: {self.score2}')

    if self.wins is not None:
      print('Significance test.')
      wins, sys1_stats, sys2_stats = self.wins, self.sys1_stats, self.sys2_stats
      print('Win ratio: Sys1=%.3f, Sys2=%.3f, tie=%.3f' % (wins[0], wins[1], wins[2]))
      if wins[0] > wins[1]:
        print('(Sys1 is superior with p value p=%.3f)\n' % (1-wins[0]))
      elif wins[1] > wins[0]:
        print('(Sys2 is superior with p value p=%.3f)\n' % (1-wins[1]))

      print('Sys1: mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
              (sys1_stats['mean'], sys1_stats['median'], sys1_stats['lower_bound'], sys1_stats['upper_bound']))
      print('Sys2: mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
              (sys2_stats['mean'], sys2_stats['median'], sys2_stats['lower_bound'], sys2_stats['upper_bound']))
    print()
    
  def plot(self, output_directory='outputs', output_fig_file='score', output_fig_format='pdf'):
    self.output_fig_file = output_fig_file
    if self.wins is not None:
      wins, sys1_stats, sys2_stats = self.wins, self.sys1_stats, self.sys2_stats
      mean, lrb, urb = sys1_stats['mean'], sys1_stats['lower_bound'], sys1_stats['upper_bound']
      sys1 = [self.score1, mean, sys1_stats['median']]
      N = len(sys1)
      sys1_err = np.zeros((2, N))
      sys1_err[0, 0] = self.score1 - lrb 
      sys1_err[1, 0] = urb - self.score1
      mean, lrb, urb = sys2_stats['mean'], sys2_stats['lower_bound'], sys2_stats['upper_bound']
      sys2 = [self.score2, sys2_stats['mean'], sys2_stats['median']]
      sys2_err = np.zeros((2, N))
      sys2_err[0, 0] = self.score2 - lrb 
      sys2_err[1, 0] = urb - self.score2
      xticklabels = [self.scorer_name, 'Bootstrap Mean', 'Bootstrap Median']
    else:
      sys1 = [self.score1]
      sys2 = [self.score2]
      sys1_err = sys2_err = None
      xticklabels = None

    make_bar_chart([sys1, sys2],
                   output_directory, output_fig_file, output_fig_format=output_fig_format,
                   errs=[sys1_err, sys2_err], title='Score Comparison', ylabel=self.scorer_name,
                   xticklabels=xticklabels)
    
  def html_content(self, output_directory):
    table = [['Sys1', 'Sys2']]
    if self.str1 is not None:
      table.append([f'{self.score1:.4f} ({self.str1})', f'{self.score2:.4f} ({self.str2})'])
    else:
      table.append([f'{self.score1:.4f} ', f'{self.score2:.4f}'])
    html = html_table(table, caption=self.scorer_name)
    if self.wins is not None:
      wins, sys1_stats, sys2_stats = self.wins, self.sys1_stats, self.sys2_stats
      table = [['Metric', 'Sys1', 'Sys2'],
               ['Win ratio', f'{wins[0]:.3f}', f'{wins[1]:.3f}'],
               ['Mean', f"{sys1_stats['mean']:.3f}", f"{sys2_stats['mean']:.3f}"],
               ['Median', f"{sys1_stats['median']:.3f}", f"{sys2_stats['median']:.3f}"],
               ['95% confidence interval', 
                f"[{sys1_stats['lower_bound']:.3f},{sys1_stats['upper_bound']:.3f}]", 
                f"[{sys2_stats['lower_bound']:.3f},{sys2_stats['upper_bound']:.3f}]"]]
      html += html_table(table, caption='Significance Test') 
    self.plot(output_directory, self.output_fig_file, 'png')
    html += html_img_reference(self.output_fig_file, 'Score Comparison')
    return html
    
class WordReport(Report):
  def __init__(self, bucketer, matches1, matches2, acc_type, header):
    self.bucketer = bucketer
    self.matches1 = [m for m in matches1]
    self.matches2 = [m for m in matches2]
    self.acc_type = acc_type
    self.header = header 
    self.acc_type_map = {'prec': 3, 'rec': 4, 'fmeas': 5}
    self.output_fig_file = None
    self.output_fig_format = None

  def print(self):
    acc_type_map = self.acc_type_map
    bucketer, matches1, matches2, acc_type, header = self.bucketer, self.matches1, self.matches2, self.acc_type, self.header
    self.print_header(header)
    acc_types = acc_type.split('+')
    for at in acc_types:
      if at not in acc_type_map:
        raise ValueError(f'Unknown accuracy type {at}')
      aid = acc_type_map[at]
      print(f'--- word {acc_type} by {bucketer.name()} bucket')
      for bucket_str, match1, match2 in zip(bucketer.bucket_strs, matches1, matches2):
        print("{}\t{:.4f}\t{:.4f}".format(bucket_str, match1[aid], match2[aid]))
      print()

  def plot(self, output_directory='outputs', output_fig_file='word-acc', output_fig_format='pdf'):
    width = 0.35
    self.output_fig_file = output_fig_file
    self.output_fig_format = output_fig_format
    acc_types = self.acc_type.split('+')
    for at in acc_types:
      if at not in self.acc_type_map:
        raise ValueError(f'Unknown accuracy type {at}')
      aid = self.acc_type_map[at]
      sys1 = [match1[aid] for match1 in self.matches1]
      sys2 = [match2[aid] for match2 in self.matches2]
      xticklabels = [s for s in self.bucketer.bucket_strs] 

      make_bar_chart([sys1, sys2],
                     output_directory, output_fig_file, output_fig_format=output_fig_format,
                     title='Word Accuracy Comparison', ylabel=at,
                     xticklabels=xticklabels)
    
  def html_content(self, output_directory):
    acc_type_map = self.acc_type_map
    bucketer, matches1, matches2, acc_type, header = self.bucketer, self.matches1, self.matches2, self.acc_type, self.header
    acc_types = acc_type.split('+') 
    
    self.plot(output_directory, self.output_fig_file, 'png')

    html = ''
    for at in acc_types:
      if at not in acc_type_map:
        raise ValueError(f'Unknown accuracy type {at}')
      aid = acc_type_map[at]
      caption = f'Word {acc_type} by {bucketer.name()} bucket'
      table = [[bucketer.name(), 'Sys1', 'Sys2']]
      table += [[bs, f'{m1[aid]:.4f}', f'{m2[aid]:.4f}'] for bs, m1, m2 in zip(bucketer.bucket_strs, matches1, matches2)]
      html += html_table(table, caption)
      html += html_img_reference(f'{self.output_fig_file}-{at}', self.header)
    return html 

class NgramReport(Report):
  def __init__(self, scorelist, report_length, min_ngram_length, max_ngram_length, matches1, matches2, compare_type, alpha, label_files=None):
    self.scorelist = scorelist
    self.report_length = report_length 
    self.min_ngram_length = min_ngram_length
    self.max_ngram_length = max_ngram_length
    self.matches1 = matches1 
    self.matches2 = matches2 
    self.compare_type = compare_type 
    self.label_files = label_files
    self.alpha = alpha
    self.output_fig_file = None

  def print(self):
    report_length = self.report_length
    self.print_header('N-gram Difference Analysis')
    print(f'--- min_ngram_length={self.min_ngram_length}, max_ngram_length={self.max_ngram_length}')
    print(f'    report_length={report_length}, alpha={self.alpha}, compare_type={self.compare_type}')
    if self.label_files is not None:
      print(self.label_files)

    print(f'--- {report_length} n-grams that System 1 had higher {self.compare_type}')
    for k, v in self.scorelist[:report_length]:
      print('{}\t{} (sys1={}, sys2={})'.format(' '.join(k), v, self.matches1[k], self.matches2[k]))
    print(f'\n--- {report_length} n-grams that System 2 had higher {self.compare_type}')
    for k, v in reversed(self.scorelist[-report_length:]):
      print('{}\t{} (sys1={}, sys2={})'.format(' '.join(k), v, self.matches1[k], self.matches2[k]))
    print()

  def plot(self, output_directory='outputs', output_fig_file='score', output_fig_format='pdf'):
    pass 

  def html_content(self, output_directory=None):
    report_length = self.report_length
    html = tag_str('p', f'min_ngram_length={self.min_ngram_length}, max_ngram_length={self.max_ngram_length}')
    html += tag_str('p', f'report_length={report_length}, alpha={self.alpha}, compare_type={self.compare_type}')
    if self.label_files is not None:
      html += tag_str('p', self.label_files)

    caption = f'{report_length} n-grams that System 1 had higher {self.compare_type}'
    table = [['n-gram', self.compare_type, 'Sys1', 'Sys2']]
    table.extend([[' '.join(k), f'{v:.2f}', self.matches1[k], self.matches2[k]] for k, v in self.scorelist[:report_length]])
    html += html_table(table, caption)

    caption = f'{report_length} n-grams that System 2 had higher {self.compare_type}'
    table = [['n-gram', self.compare_type, 'Sys1', 'Sys2']]
    table.extend([[' '.join(k), f'{v:.2f}', self.matches1[k], self.matches2[k]] for k, v in reversed(self.scorelist[-report_length:])])
    html += html_table(table, caption)
    return html 

class SentenceReport(Report):
  def __init__(self, bucketer=None, bucket_type=None, sys1_stats=None, sys2_stats=None, statistic_type=None, score_measure=None):
    self.bucketer = bucketer
    self.bucket_type = bucket_type 
    self.sys1_stats = [s for s in sys1_stats]
    self.sys2_stats = [s for s in sys2_stats] 
    self.statistic_type = statistic_type
    self.score_measure = score_measure
    self.output_fig_file = None

  def print(self):
    bucketer, stats1, stats2, bucket_type, statistic_type, score_measure = self.bucketer, self.sys1_stats, self.sys2_stats, self.bucket_type, self.statistic_type, self.score_measure
    self.print_header('Sentence Bucket Analysis')
    print(f'--- bucket_type={bucket_type}, statistic_type={statistic_type}, score_measure={score_measure}')
    for bs, s1, s2 in zip(bucketer.bucket_strs, stats1, stats2):
      print(f'{bs}\t{s1}\t{s2}')
    print()

  def plot(self, output_directory='outputs', output_fig_file='word-acc', output_fig_format='pdf'):
    self.output_fig_file = output_fig_file
    sys1 = self.sys1_stats
    sys2 = self.sys2_stats
    xticklabels = [s for s in self.bucketer.bucket_strs] 

    make_bar_chart([sys1, sys2],
                   output_directory, output_fig_file, output_fig_format=output_fig_format,
                   title='Sentence Bucket Analysis', xlabel=self.bucket_type, ylabel=self.statistic_type,
                   xticklabels=xticklabels)

  def html_content(self, output_directory=None):
    bucketer, stats1, stats2, bucket_type, statistic_type, score_measure = self.bucketer, self.sys1_stats, self.sys2_stats, self.bucket_type, self.statistic_type, self.score_measure
    caption = (f'bucket_type={bucket_type}, statistic_type={statistic_type}, score_measure={score_measure}')
    table = [[bucket_type, 'Sys1', 'Sys2']]
    table.extend([[bs, f'{s1:.4f}', f'{s2:.4f}'] for bs, s1, s2 in zip(bucketer.bucket_strs, stats1, stats2)])
    html = html_table(table, caption)
    self.plot(output_directory, self.output_fig_file, 'png')
    html += html_img_reference(self.output_fig_file, 'Sentence Bucket Analysis')
    return html 

class SentenceExampleReport(Report):
  def __init__(self, report_length=None, scorediff_list=None, scorer_name=None, ref=None, out1=None, out2=None):
    self.report_length = report_length 
    self.scorediff_list = scorediff_list
    self.scorer_name = scorer_name
    self.ref = ref 
    self.out1 = out1 
    self.out2 = out2

  def print(self):
    report_length = self.report_length
    ref, out1, out2 = self.ref, self.out1, self.out2
    print(f'--- {report_length} sentences where Sys1>Sys2 at {self.scorer_name}')
    for bdiff, s1, s2, str1, str2, i in self.scorediff_list[:report_length]:
      print ('sys2-sys1={}, sys1={}, sys2={}\nRef:  {}\nSys1: {}\nSys2: {}\n'.format(bdiff, s1, s2, ' '.join(ref[i]), ' '.join(out1[i]), ' '.join(out2[i])))
    print(f'--- {report_length} sentences where Sys2>Sys1 at {self.scorer_name}')
    for bdiff, s1, s2, str1, str2, i in self.scorediff_list[-report_length:]:
      print ('sys2-sys1={}, sys1={}, sys2={}\nRef:  {}\nSys1: {}\nSys2: {}\n'.format(bdiff, s1, s2, ' '.join(ref[i]), ' '.join(out1[i]), ' '.join(out2[i])))


  def plot(self, output_directory='outputs', output_fig_file='word-acc', output_fig_format='pdf'):
    pass 

  def html_content(self, output_directory=None):
    report_length = self.report_length 
    ref, out1, out2 = self.ref, self.out1, self.out2
    html = tag_str('h4', f'{report_length} sentences where Sys1>Sys2 at {self.scorer_name}')
    for bdiff, s1, s2, str1, str2, i in self.scorediff_list[:report_length]:
      caption = f'sys2-sys1={bdiff:.2f}, sys1={s1:.2f}, sys2={s2:.2f}'
      table = [['Ref', ' '.join(ref[i])], ['Sys1', ' '.join(out1[i])], ['Sys2', ' '.join(out2[i])]]
      html += html_table(table, caption)

    html += tag_str('h4', f'{report_length} sentences where Sys2>Sys1 at {self.scorer_name}')
    for bdiff, s1, s2, str1, str2, i in self.scorediff_list[-report_length:]:
      caption = f'sys2-sys1={bdiff:.2f}, sys1={s1:.2f}, sys2={s2:.2f}'
      table = [['Ref', ' '.join(ref[i])], ['Sys1', ' '.join(out1[i])], ['Sys2', ' '.join(out2[i])]]
      html += html_table(table, caption)
    return html 


def tag_str(tag, str, new_line=''):
  return f'<{tag}>{new_line} {str} {new_line}</{tag}>'

def html_table(table, caption=None):
  html = '<table border="1">\n'
  if caption is not None:
    html += tag_str('caption', caption)
  html += '\n  '.join(tag_str('th', ri) for ri in table[0])
  for row in table[1:]:
    table_row = '\n  '.join(tag_str('td', ri) for ri in row)
    html += tag_str('tr', table_row)
  html += '\n</table>\n <br>'
  return html

def generate_html_report(reports, output_directory):
  content = []
  for name, rep in reports:
    content.append(f'<h2>{name}</h2>')
    for r in rep:
      content.append(r.html_content(output_directory))
  content = "\n".join(content)
  
  if not os.path.exists(output_directory):
        os.makedirs(output_directory)
  html_file = os.path.join(output_directory, 'index.html')
  with open(html_file, 'w') as f:
    message = (f'<html>\n<head>\n<link rel="stylesheet" href="compare_mt.css">\n</head>\n'+
               f'<script>\n{javascript_style}\n</script>\n'+
               f'<body>\n<h1>compare_mt.py Analysis Report</h1>\n {content} \n</body>\n</html>')
    f.write(message)
  css_file = os.path.join(output_directory, 'compare_mt.css')
  with open(css_file, 'w') as f:
    f.write(css_style)
  