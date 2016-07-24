#########################################
# Mediation Analysis
#
# Interfaces with FeatureWorker and Statsmodels
#
# example usage: ./fwInterface.py -d DATABASE -t TABLE -c GROUP_BY --mediation \
#                --outcome_table OUTCOME_TABLE_NAME
#                --path_starts PATH_START_1 ... PATH_START_J \
#                --mediators
#                --outcomes OUTCOME_1 ... OUTCOME_K \
#                -f FEATURE_TABLE [-features FEATURE_1 ... FEATURE_I] \
#                [-controls CONTROL_1 ... CONTROLS_L] \
#                [--feat_as_path_start or --feat_as_outcome or --feat_as_control or --no_features] \
#                [--mediation_boot] \
#                [--group_freq_thresh GROUP_THRESH] \
#                [--output_name OUTPUT_NAME]

import numpy as np
import pandas as pd
from statsmodels.graphics.utils import maybe_name_or_idx
import statsmodels.api as sm
import scipy.stats as st
import csv
import collections
import patsy
from math import sqrt
from scipy.stats import zscore
from scipy.stats.stats import pearsonr, spearmanr
from fwConstants import pCorrection, DEF_P
from operator import itemgetter
import itertools
import sys

MAX_SUMMARY_SIZE = 10 # maximum number of results to print in summary for each path start / outcome pair

class MediationAnalysis:
	"""
	Interface between Mediation class and fwInterface
	flow of switches:
		--path_starts
		--outcomes
		--mediators
		default: --path_starts from -outcome_table
				 --mediators from -f
				 --outcomes from -outcome_table
		--feat_as_path_start: --path_starts from -f
							  --mediators from -outcome_table
							  --outcomes from -outcome_table
							  --controls from -outcome_table
		--feat_as_outcome:  --path_starts from -outcome_table
							--mediators from -outcome_table
							--outcomes from -f
							--controls from -outcome_table
		--feat_as_control:  --path_starts from -outcome_table
							--mediators from -outcome_table
							--outcomes from -outcome_table
							--controls from -f
		--no_features:  --path_starts from -outcome_table
						--mediators from -outcome_table
						--outcomes from -outcome_table
						--controls from -outcome_table
	"""

	def __init__(self, fg, og, path_starts, mediators, outcomes, controls, method="parametric", boot_number=1000, sig_level=DEF_P, style='baron'):

		self.outcomeGetter = og
		self.featureGetter = fg

		self.pathStartNames = path_starts
		self.mediatorNames = mediators
		self.outcomeNames = outcomes
		self.controlNames = controls

		self.mediation_method = method
		self.boot_number = boot_number
		self.sig_level = sig_level

		self.output = dict()
		self.output_sobel = dict()
		self.output_p = dict() # [c_p, c'_p, alpha_p, beta_p, sobel_p, ...]

		if style == 'baron':
			self.baron_and_kenny = True
			self.imai_and_keele = False
		elif style == 'imai':
			self.baron_and_kenny = False
			self.imai_and_keele = True
		elif style == 'both':
			self.baron_and_kenny = True
			self.imai_and_keele = True

	def _truncate_groups(seq, max_group_size, key):
		"""yield only the first `max_group_size` elements from each sub-group of `seq`"""
		for key, group in itertools.groupby(seq, key):
			for item in list(group)[:max_group_size]:
				yield item

	def print_summary(self, output_name=''):
		summary_results = []
		if output_name:
			if ".csv" in output_name:
				csv_name = output_name.replace(".csv", "_summary.csv")
			else:
				csv_name = output_name + "_summary.csv"
		else:
			csv_name = "mediation_summary.csv"

		header = ["Path Start", "Outcome", "Mediator"]
		if self.baron_and_kenny:
			header = header + ["c-c'", "sobel_P", "alpha", "beta", "c'"]
		if self.imai_and_keele:
			header = header + ["Prop_mediated_average_Estimate", "Prop_mediated_average_P_value",
				"ACME_average_Estimate", "ACME_average_P_value"]

		for path_start in self.output:
			for outcome in self.output[path_start]:
				count = 0
				for mediator in self.output[path_start][outcome]:
					sobel_p = self.output_p[path_start][outcome][mediator][4]
					if sobel_p <= self.sig_level:
						results = [path_start, outcome, mediator]
						if self.baron_and_kenny:
							results = results + [self.output_sobel[path_start][outcome][mediator].tolist()[4] , sobel_p] + \
								[self.output_sobel[path_start][outcome][mediator].tolist()[6],
								self.output_sobel[path_start][outcome][mediator].tolist()[9],
								self.output_sobel[path_start][outcome][mediator].tolist()[2]]
						if self.imai_and_keele:
							results = results + [self.output[path_start][outcome][mediator][0],
								self.output_p[path_start][outcome][mediator][5],
								self.output[path_start][outcome][mediator][4],
								self.output_p[path_start][outcome][mediator][6]]
						summary_results.append(results)


		summary_results.sort(key=lambda x: (x[0].lower(), x[1].lower(), -abs(x[3])), reverse=False)
		if len(summary_results) > 0:
			print "Printing results to: %s" % csv_name
			with open(csv_name, 'wb') as csvfile:
				f = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, delimiter=',')
				f.writerow(header)
				for key, group in itertools.groupby(summary_results, key=lambda x: (x[0], x[1])):
					for item in list(group)[:MAX_SUMMARY_SIZE]:
						f.writerow(item)
		else:
			print "Summary: nothing passes significance threshold of %s." % (self.sig_level)


	def print_csv(self, output_name=''):
		if output_name:
			csv_name = output_name
		else:
			csv_name = "mediation.csv"

		header = ["Path Start", "Outcome", "Mediator"]
		if self.baron_and_kenny:
			header = header + ["c", "c_p", "c'", "c'_p", "c-c'", "alpha*beta", "alpha", "alpha_error", "alpha_p",
				"beta", "beta_error", "beta_p", "sobel", "sobel_SE", "sobel_P"]
		if self.imai_and_keele:
			header = header + ["Prop_mediated_average_Estimate", "Prop_mediated_average_P_value",
				"ACME_average_Estimate", "ACME_average_P_value",
				"ADE_average_Estimate", "ADE_average_P_value",
				"Prop_mediated_average_Lower_CI_bound", "Prop_mediated_average_Upper_CI_bound",
				"ACME_average_Lower_CI_bound", "ACME_average_Upper_CI_bound",
				"ADE_average_Lower_CI_bound", "ADE_average_Upper_CI_bound",
				"ACME_treated_Estimate", "ACME_treated_P_value", "ACME_treated_Lower_CI_bound", "ACME_treated_Upper_CI_bound",
				"ACME_control_Estimate", "ACME_control_P_value", "ACME_control_Lower_CI_bound", "ACME_control_Upper_CI_bound",
				"ADE_treated_Estimate", "ADE_treated_P_value","ADE_treated_Lower_CI_bound", "ADE_treated_Upper_CI_bound",
				"ADE_control_Estimate", "ADE_control_P_value", "ADE_control_Lower_CI_bound", "ADE_control_Upper_CI_bound",
				"Total_effect_Estimate", "Total_effect_P_value", "Total_effect_Lower_CI_bound", "Total_effect_Upper_CI_bound",
				"Prop_mediated_control_Estimate", "Prop_mediated_control_P_value", "Prop_mediated_control_Lower_CI_bound", "Prop_mediated_control_Upper_CI_bound",
				"Prop_mediated_treated_Estimate", "Prop_mediated_treated_P_value", "Prop_mediated_treated_Lower_CI_bound", "Prop_mediated_treated_Upper_CI_bound"]

		print "Printing results to: %s" % csv_name
		with open(csv_name, 'wb') as csvfile:
			f = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, delimiter=',')
			f.writerow(header)
			for path_start in self.output:
				for outcome in self.output[path_start]:
					for mediator in self.output[path_start][outcome]:
						bk_rearranged = []
						med_rearranged = []
						p_list = self.output_p[path_start][outcome][mediator]
						if self.baron_and_kenny:
							bk_rearranged = [self.output_sobel[path_start][outcome][mediator][0], p_list[0], self.output_sobel[path_start][outcome][mediator][2], p_list[1],
											self.output_sobel[path_start][outcome][mediator][4], self.output_sobel[path_start][outcome][mediator][5],
											self.output_sobel[path_start][outcome][mediator][6], self.output_sobel[path_start][outcome][mediator][7], p_list[2],
											self.output_sobel[path_start][outcome][mediator][9], self.output_sobel[path_start][outcome][mediator][10], p_list[3],
											self.output_sobel[path_start][outcome][mediator][12], self.output_sobel[path_start][outcome][mediator][13], p_list[4]]
						if self.imai_and_keele:
							med_rearranged = [self.output[path_start][outcome][mediator][0], p_list[5],
												self.output[path_start][outcome][mediator][4], p_list[6],
												self.output[path_start][outcome][mediator][8], p_list[7]] \
												 + self.output[path_start][outcome][mediator][2:4] +  self.output[path_start][outcome][mediator][6:8] +  self.output[path_start][outcome][mediator][10:12] \
												 + [self.output[path_start][outcome][mediator][12], p_list[8]] + self.output[path_start][outcome][mediator][14:16] \
												 + [self.output[path_start][outcome][mediator][16], p_list[9]] + self.output[path_start][outcome][mediator][18:20] \
												 + [self.output[path_start][outcome][mediator][20], p_list[10]] + self.output[path_start][outcome][mediator][22:24] \
												 + [self.output[path_start][outcome][mediator][24], p_list[11]] + self.output[path_start][outcome][mediator][26:28] \
												 + [self.output[path_start][outcome][mediator][28], p_list[12]] + self.output[path_start][outcome][mediator][30:32] \
												 + [self.output[path_start][outcome][mediator][32], p_list[13]] + self.output[path_start][outcome][mediator][34:36] \
												 + [self.output[path_start][outcome][mediator][36], p_list[14]] + self.output[path_start][outcome][mediator][38:]
						f.writerow([path_start, outcome, mediator] + bk_rearranged + med_rearranged)


	def prep_data(self, path_start, mediator, outcome, controlDict=None, controlNames=None, zscoreRegression=None):
		"""
		Take dictionary data and return a Pandas DataFrame indexed by group_id.
		Column names are 'path_start', 'mediator' and 'outcome'
		"""
		ps_df = pd.DataFrame(data=collections.OrderedDict(sorted(path_start.items())).items(), columns=['group_id', 'path_start']).set_index(['group_id']).fillna(0)
		m_df = pd.DataFrame(data=mediator.items(), columns=['group_id', 'mediator']).set_index(['group_id'])
		o_df = pd.DataFrame(data=outcome.items(), columns=['group_id', 'outcome']).set_index(['group_id'])

		data = ps_df.join(m_df)
		data = data.join(o_df)
		if controlDict and controlNames:
			for control in controlNames:
				data = data.join(pd.DataFrame(data=controlDict[control].items(), columns=['group_id', control]).set_index(['group_id']))
		data = data.dropna()
		return data

	def get_data(self, switch, outcome_field, location, features):
		"""
		get data from outcomeGetter / featureGetter
		"""
		data = None
		if switch == "feat_as_path_start" and location == "path_start":
				data = features[outcome_field]
		elif switch == "feat_as_outcome" and location == "outcome":
				data = features[outcome_field]
		elif switch == "feat_as_control" and location == "control":
				data = features[outcome_field]
		elif switch == "default" and location == "mediator":
				data = features[outcome_field]
		else:
			data = dict((x, y) for x, y in self.outcomeGetter.getGroupAndOutcomeValues(outcomeField = outcome_field))
		return data

	def mediate(self, group_freq_thresh = 0, switch="default", spearman = False, bonferroni = False, p_correction_method = 'BH',
				zscoreRegression = True, logisticReg = False):
		"""
		output =    {path_start_i:
						{outcome_j:
							{mediator_k:
								["ACME (control)", "ACME (treated)", "ADE (control)", "ADE (treated)",
								 "Total effect", "Prop. mediated (control)", "Prop. mediated (treated)",
								 "ACME (average)", "ADE (average)", "Prop. mediated (average)"]
								X
								["Estimate", "Lower CI bound", "Upper CI bound", "P-value"]
							}
						}
					}
		"""

		if "no_features" not in switch:
			(groups, allOutcomes, controls) = self.outcomeGetter.getGroupsAndOutcomes(group_freq_thresh)

		if self.featureGetter:
			(allFeatures, featureNames) = self.featureGetter.getGroupNormsWithZerosFeatsFirst(groups=groups)

		if switch == "feat_as_path_start":
			if len(self.pathStartNames) == 0:
				self.pathStartNames = allFeatures.keys()
			numMeds = len(self.pathStartNames)

		elif switch == "feat_as_outcome":
			if len(self.outcomeNames) == 0:
				self.outcomeNames = allFeatures.keys()
			numMeds = len(self.outcomeNames)

		elif switch == "feat_as_control":
			if len(self.controlNames) == 0:
				self.controlNames = allFeatures.keys()
			numMeds = len(self.pathStartNames)

		elif switch == "no_features":
			numMeds = len(self.pathStartNames)

		elif switch == "default":
			if len(self.mediatorNames) == 0:
				self.mediatorNames = allFeatures.keys()
			numMeds = len(self.mediatorNames)

		mediation_count = 0
		total_mediations = str(len(self.pathStartNames)*len(self.mediatorNames)*len(self.outcomeNames))

		for path_start in self.pathStartNames:
			self.output[path_start] = {}
			self.output_sobel[path_start] = {}
			self.output_p[path_start] = {}

			for outcome in self.outcomeNames:
				self.output[path_start][outcome] = {}
				self.output_sobel[path_start][outcome] = {}
				self.output_p[path_start][outcome] = {}

				for mediator in self.mediatorNames:
					mediation_count += 1
					self.output_p[path_start][outcome][mediator] = []
					self.output[path_start][outcome][mediator] = []

					if len(self.controlNames) > 0:
						#data = self.prep_data(pathstartsDict[path_start], mediatorsDict[mediator], outcomesDict[outcome], controlsDict, self.controlNames, zscoreRegression=zscoreRegression)
						data = self.prep_data(self.get_data(switch, path_start, "path_start", allFeatures),
							self.get_data(switch, mediator, "mediator", allFeatures),
							self.get_data(switch, outcome, "outcome", allFeatures),
							controlsDict, self.controlNames, zscoreRegression=zscoreRegression)

						control_formula = " + " + " + ".join(self.controlNames)
					else:
						#data = self.prep_data(pathstartsDict[path_start], mediatorsDict[mediator], outcomesDict[outcome], zscoreRegression=zscoreRegression)
						data = self.prep_data(self.get_data(switch, path_start, "path_start", allFeatures),
							self.get_data(switch, mediator, "mediator", allFeatures),
							self.get_data(switch, outcome, "outcome", allFeatures),
							zscoreRegression=zscoreRegression)

						control_formula = ""

					outcome_exog = patsy.dmatrix("mediator + path_start " + control_formula + " -1", data,
													  return_type='dataframe')
					mediator_exog = patsy.dmatrix("path_start " + control_formula + " -1", data,
											 return_type='dataframe')
					direct_exog = patsy.dmatrix("path_start " + control_formula + " -1", data,
											 return_type='dataframe')

					if zscoreRegression:
						outcome_array = np.asarray(data['outcome']) if logisticReg else np.asarray(zscore(data['outcome']))
						mediator_array = np.asarray(data['mediator']) if logisticReg else np.asarray(zscore(data['mediator']))
						outcome_exog['mediator'] = zscore(outcome_exog['mediator'])
						outcome_exog['path_start'] = zscore(outcome_exog['path_start'])
						mediator_exog['path_start'] = zscore(mediator_exog['path_start'])
						direct_exog['path_start'] = zscore(direct_exog['path_start'])
					else:
						outcome_array = np.asarray(data['outcome'])
						mediator_array = np.asarray(data['mediator'])

					outcome_model = sm.OLS(outcome_array, outcome_exog)
					mediator_model = sm.OLS(mediator_array, mediator_exog)
					direct_model = sm.OLS(outcome_array, direct_exog)

					# classic mediation with Sobel Test
					if self.baron_and_kenny:
						outcome_results = outcome_model.fit()
						mediator_results = mediator_model.fit()
						direct_results = direct_model.fit()

						c = direct_results.params.get('path_start')
						c_prime = outcome_results.params.get('path_start')
						alpha = mediator_results.params.get('path_start')
						alpha_error = mediator_results.bse.get('path_start')
						beta = outcome_results.params.get('mediator')
						beta_error = outcome_results.bse.get('mediator')
						sobel_SE = sqrt(beta*beta*alpha_error*alpha_error + alpha*alpha*beta_error*beta_error)
						sobel = (alpha*beta)/ sobel_SE

						if bonferroni:
							c_p = direct_results.pvalues.get('path_start')*numMeds
							c_prime_p = outcome_results.pvalues.get('path_start')*numMeds
							alpha_p = mediator_results.pvalues.get('path_start')*numMeds
							beta_p = outcome_results.pvalues.get('mediator')*numMeds
							sobel_p = st.norm.sf(abs(sobel))*2*numMeds
						else:
							c_p = direct_results.pvalues.get('path_start')
							c_prime_p = outcome_results.pvalues.get('path_start')
							alpha_p = mediator_results.pvalues.get('path_start')
							beta_p = outcome_results.pvalues.get('mediator')
							sobel_p = st.norm.sf(abs(sobel))*2

						self.output_sobel[path_start][outcome][mediator] = np.array([c, c_p, c_prime, c_prime_p, c-c_prime, alpha*beta, alpha, alpha_error, alpha_p, beta, beta_error, beta_p, sobel, sobel_SE, sobel_p])
						self.output_p[path_start][outcome][mediator] = self.output_p[path_start][outcome][mediator] + [c_p, c_prime_p, alpha_p, beta_p, sobel_p ]

					# new mediation NOT IMPLEMENTED
					if self.imai_and_keele:
						# tx_pos = [outcome_exog.columns.tolist().index("path_start"),
						# 		  mediator_exog.columns.tolist().index("path_start")]
						# med_pos = outcome_exog.columns.tolist().index("mediator")

						# med = Mediation(outcome_model, mediator_model, tx_pos, med_pos)

						# med_result = med.fit(method=self.mediation_method, n_rep=self.boot_number)
						# summary = med_result.summary(bonferroni = bonferroni, numMeds=numMeds)
						# summary_array = np.reshape(summary.values, 40).tolist()

						# self.output[path_start][outcome][mediator] = summary_array
						# self.output_p[path_start][outcome][mediator] = self.output_p[path_start][outcome][mediator] + summary["P-value"].tolist()

						print "Mediation number " + str(mediation_count) + " out of " + total_mediations

					if len(self.controlNames) > 0:
						print "Path Start: %s, Mediator: %s, Outcome: %s, Controls: %s" % (path_start, mediator, outcome, ", ".join(self.controlNames))
					else:
						print "Path Start: %s, Mediator: %s, Outcome: %s" % (path_start, mediator, outcome)
					if self.baron_and_kenny:
						print "C: %s, C_p: %s, C': %s, C'_p: %s" % (str(c), str(c_p), str(c_prime), str(c_prime_p))
						print "C-C': %s, alpha*beta: %s" % (str(c-c_prime), str(alpha*beta))
						print "alpha: %s, alpha_error: %s, alpha_p: %s" % (str(alpha), str(alpha_error), str(alpha_p))
						print "beta: %s, beta_error: %s, beta_p: %s" % (str(beta), str(beta_error), str(beta_p))
						print "Sobel z-score: %s, Sobel SE: %s, Sobel p: %s" % (str(sobel), str(sobel_SE), str(sobel_p))
					if self.imai_and_keele:
						print summary
					print ""

		if p_correction_method:
			p_list = []
			if self.baron_and_kenny:
				p_list = p_list + ["C_p", "C'_p", "alpha_p", "beta_p", "sobel_p"]
			if self.imai_and_keele:
				p_list = p_list + ["Prop_mediated_average_P_value", "ACME_average_P_value", "ADE_average_P_value", "ACME_treated_P_value",
					"ACME_control_P_value", "ADE_treated_P_value", "ADE_control_P_value", "Total_effect_P_value",
					"Prop_mediated_control_P_value", "Prop_mediated_treated_P_value"]
			p_dict = dict()
			r_dict = dict()
			for path_start in self.pathStartNames:
				for outcome in self.outcomeNames:
					for i, p in enumerate(p_list):
						p_dict[p] = dict()
						for mediator in self.mediatorNames:
							p_dict[p][mediator] = self.output_p[path_start][outcome][mediator][i]
						p_dict[p] = pCorrection(p_dict[p], p_correction_method, [0.05, 0.01, 0.001], rDict = None)
					for mediator in self.mediatorNames:
						self.output_p[path_start][outcome][mediator] = [p_dict[p][mediator] for p in p_list]
