import json
import re
import os
import gradio as gr
import dotenv
from fireworks.client import Fireworks

extraction_example = [["Llama 3.1 8B (Finetuned for extraction)",
                       "Question: How much was Dow Inc's Cash Flow Margin for the Fiscal Year concluding in FY 2020?  Answer with a formula substituted with values.",
                       "<us-gaap:RestructuringSettlementAndImpairmentProvisions xmlns:us- >708000000</> \n<us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax xmlns:us- >38542000000</> \n<us-gaap:CostOfGoodsAndServicesSold xmlns:us- >33346000000</> \n<us-gaap:ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost xmlns:us- >768000000</> \n<us-gaap:SellingGeneralAndAdministrativeExpense xmlns:us- >1471000000</> \n<us-gaap:AmortizationOfIntangibleAssets xmlns:us- >401000000</> \n<us-gaap:RestructuringSettlementAndImpairmentProvisions xmlns:us- >708000000</> \n<us-gaap:IncomeLossFromEquityMethodInvestments xmlns:us- >-18000000</> \n<us-gaap:NonoperatingIncomeExpense xmlns:us- >1269000000</> \n<us-gaap:InterestIncomeOther xmlns:us- >38000000</> \n<us-gaap:InterestExpenseDebt xmlns:us- >827000000</> \n<us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest xmlns:us- >2071000000</> \n<us-gaap:IncomeTaxExpenseBenefit xmlns:us- >777000000</> \n<us-gaap:IncomeLossFromContinuingOperations xmlns:us- >1294000000</> \n<us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity xmlns:us- >0</> \n<us-gaap:ProfitLoss xmlns:us- >1294000000</> \n<us-gaap:NetIncomeLossAttributableToNoncontrollingInterest xmlns:us- >69000000</> \n<us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic xmlns:us- >1225000000</> \n<us-gaap:IncomeLossFromContinuingOperationsPerBasicShare xmlns:us- >1.64</> \n<us-gaap:DiscontinuedOperationIncomeLossFromDiscontinuedOperationNetOfTaxPerBasicShare xmlns:us- >0</> \n<us-gaap:EarningsPerShareBasic xmlns:us- >1.64</> \n<us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare xmlns:us- >1.64</> \n<us-gaap:DiscontinuedOperationIncomeLossFromDiscontinuedOperationNetOfTaxPerDilutedShare xmlns:us- >0</> \n<us-gaap:EarningsPerShareDiluted xmlns:us- >1.64</> \n<us-gaap:WeightedAverageNumberOfSharesOutstandingBasic xmlns:us- >740500000</> \n<us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding xmlns:us- >742300000</> \n<us-gaap:ProfitLoss xmlns:us- >1294000000</> \n<us-gaap:OtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentNetOfTax xmlns:us- >40000000</> \n<us-gaap:OtherComprehensiveIncomeLossForeignCurrencyTransactionAndTranslationAdjustmentNetOfTax xmlns:us- >205000000</> \n<us-gaap:OtherComprehensiveIncomeLossPensionAndOtherPostretirementBenefitPlansAdjustmentNetOfTax xmlns:us- >778000000</> \n<us-gaap:OtherComprehensiveIncomeLossDerivativesQualifyingAsHedgesNetOfTax xmlns:us- >-76000000</> \n<us-gaap:OtherComprehensiveIncomeLossNetOfTax xmlns:us- >-609000000</> \n<us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest xmlns:us- >685000000</> \n<us-gaap:ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest xmlns:us- >69000000</> \n<us-gaap:ComprehensiveIncomeNetOfTax xmlns:us- >616000000</> \n<us-gaap:NetIncomeLossIncludingPortionAttributableToNonredeemableNoncontrollingInterest xmlns:us- >1294000000</> \n<us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity xmlns:us- >0</> \n<us-gaap:IncomeLossFromContinuingOperations xmlns:us- >1294000000</> \n<us-gaap:DepreciationDepletionAndAmortization xmlns:us- >2874000000</> \n<us-gaap:DeferredIncomeTaxExpenseBenefit xmlns:us- >258000000</> \n<us-gaap:IncomeLossFromEquityMethodInvestmentsNetOfDividendsOrDistributions xmlns:us- >-443000000</> \n<us-gaap:PensionAndOtherPostretirementBenefitExpense xmlns:us- >266000000</> \n<us-gaap:PensionAndOtherPostretirementBenefitContributions xmlns:us- >299000000</> \n<us-gaap:GainLossOnDispositionOfAssets1 xmlns:us- >802000000</> \n<us-gaap:RestructuringCostsAndAssetImpairmentCharges xmlns:us- >708000000</> \n<us-gaap:OtherNoncashIncomeExpense xmlns:us- >-318000000</> \n<us-gaap:IncreaseDecreaseInAccountsAndNotesReceivable xmlns:us- >-171000000</> \n<us-gaap:IncreaseDecreaseInInventories xmlns:us- >-515000000</> \n<us-gaap:IncreaseDecreaseInAccountsPayable xmlns:us- >-84000000</> \n<us-gaap:IncreaseDecreaseInOtherOperatingCapitalNet xmlns:us- >-590000000</> \n<us-gaap:NetCashProvidedByUsedInOperatingActivitiesContinuingOperations xmlns:us- >6252000000</> \n<us-gaap:CashProvidedByUsedInOperatingActivitiesDiscontinuedOperations xmlns:us- >-26000000</> \n<us-gaap:NetCashProvidedByUsedInOperatingActivities xmlns:us- >6226000000</> \n<us-gaap:PaymentsToAcquireMachineryAndEquipment xmlns:us- >1252000000</> \n<us-gaap:PaymentsToExploreAndDevelopOilAndGasProperties xmlns:us- >5000000</> \n<us-gaap:PaymentsToAcquireEquipmentOnLease xmlns:us- >5000000</> \n<us-gaap:ProceedsFromSalesOfBusinessAffiliateAndProductiveAssets xmlns:us- >929000000</> \n<us-gaap:PaymentsToAcquireBusinessesNetOfCashAcquired xmlns:us- >130000000</> \n<us-gaap:PaymentsToAcquireInvestments xmlns:us- >1203000000</> \n<us-gaap:ProceedsFromSaleAndMaturityOfOtherInvestments xmlns:us- >1122000000</> \n<us-gaap:PaymentsForProceedsFromOtherInvestingActivities xmlns:us- >-29000000</> \n<us-gaap:NetCashProvidedByUsedInInvestingActivitiesContinuingOperations xmlns:us- >-841000000</> \n<us-gaap:CashProvidedByUsedInInvestingActivitiesDiscontinuedOperations xmlns:us- >0</> \n<us-gaap:NetCashProvidedByUsedInInvestingActivities xmlns:us- >-841000000</> \n<us-gaap:ProceedsFromRepaymentsOfShortTermDebtMaturingInThreeMonthsOrLess xmlns:us- >-431000000</> \n<us-gaap:ProceedsFromShortTermDebtMaturingInMoreThanThreeMonths xmlns:us- >163000000</> \n<us-gaap:RepaymentsOfShortTermDebtMaturingInMoreThanThreeMonths xmlns:us- >163000000</> \n<us-gaap:ProceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet xmlns:us- >4672000000</> \n<us-gaap:RepaymentsOfLongTermDebtAndCapitalSecurities xmlns:us- >4653000000</> \n<us-gaap:PaymentsForRepurchaseOfCommonStock xmlns:us- >125000000</> \n<us-gaap:ProceedsFromIssuanceOfCommonStock xmlns:us- >108000000</> \n<us-gaap:PaymentsOfFinancingCosts xmlns:us- >175000000</> \n<us-gaap:PaymentsRelatedToTaxWithholdingForShareBasedCompensation xmlns:us- >27000000</> \n<us-gaap:PaymentsOfDividendsMinorityInterest xmlns:us- >62000000</> \n<us-gaap:PaymentsToMinorityShareholders xmlns:us- >0</> \n<us-gaap:PaymentsOfDividendsCommonStock xmlns:us- >2071000000</> \n<us-gaap:ProceedsFromPaymentsForOtherFinancingActivities xmlns:us- >0</> \n<us-gaap:NetCashProvidedByUsedInFinancingActivitiesContinuingOperations xmlns:us- >-2764000000</> \n<us-gaap:CashProvidedByUsedInFinancingActivitiesDiscontinuedOperations xmlns:us- >0</> \n<us-gaap:NetCashProvidedByUsedInFinancingActivities xmlns:us- >-2764000000</> \n<us-gaap:EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents xmlns:us- >107000000</> \n<us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect xmlns:us- >2728000000</> \n<us-gaap:CommonStockDividendsPerShareDeclared xmlns:us- >2.80</> \n<us-gaap:AssetRetirementObligationsPolicy xmlns:us- >Asset Retirement ObligationsThe Company records asset retirement obligations as incurred and reasona</> \n<us-gaap:Revenues xmlns:us- >38542000000</> \n<us-gaap:Revenues xmlns:us- >38542000000</> \n<us-gaap:ContractWithCustomerLiabilityRevenueRecognized xmlns:us- >145000000</> \n<us-gaap:ContractWithCustomerAssetReclassifiedToReceivable xmlns:us- >25000000</> \n<us-gaap:AssetImpairmentCharges xmlns:us- >49000000</> \n<us-gaap:DefinedBenefitPlanNetPeriodicBenefitCost xmlns:us- >-103000000</> \n<us-gaap:ForeignCurrencyTransactionGainLossBeforeTax xmlns:us- >-62000000</> \n<us-gaap:GainsLossesOnExtinguishmentOfDebt xmlns:us- >-149000000</> \n<us-gaap:GainLossOnSaleOfOtherAssets xmlns:us- >48000000</> \n<us-gaap:OtherNonoperatingIncomeExpense xmlns:us- >84000000</> \n<us-gaap:NonoperatingIncomeExpense xmlns:us- >1269000000</> \n<us-gaap:InterestPaidNet xmlns:us- >842000000</> \n<us-gaap:IncomeTaxesPaid xmlns:us- >518000000</> \n<us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic xmlns:us- >-681000000</> \n<us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign xmlns:us- >2752000000</> \n<us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest xmlns:us- >2071000000</> \n<us-gaap:CurrentFederalTaxExpenseBenefit xmlns:us- >-176000000</> \n<us-gaap:CurrentStateAndLocalTaxExpenseBenefit xmlns:us- >4000000</> \n<us-gaap:CurrentForeignTaxExpenseBenefit xmlns:us- >691000000</> \n<us-gaap:CurrentIncomeTaxExpenseBenefit xmlns:us- >519000000</> \n<us-gaap:DeferredFederalIncomeTaxExpenseBenefit xmlns:us- >184000000</> \n<us-gaap:DeferredStateAndLocalIncomeTaxExpenseBenefit xmlns:us- >19000000</> \n<us-gaap:DeferredForeignIncomeTaxExpenseBenefit xmlns:us- >55000000</> \n<us-gaap:DeferredIncomeTaxExpenseBenefit xmlns:us- >258000000</> \n<us-gaap:IncomeTaxExpenseBenefit xmlns:us- >777000000</> \n<us-gaap:IncomeLossFromContinuingOperations xmlns:us- >1294000000</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate xmlns:us- >0.210</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationEquityInEarningsLossesOfUnconsolidatedSubsidiary xmlns:us- >0.002</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationForeignIncomeTaxRateDifferential xmlns:us- >0.017</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationRepatriationOfForeignEarnings xmlns:us- >0.039</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationTaxContingencies xmlns:us- >0.033</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationChangeInDeferredTaxAssetsValuationAllowance xmlns:us- >0.126</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationTaxCutsAndJobsActOf2017Percent xmlns:us- >0</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationPriorYearIncomeTaxes xmlns:us- >0</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationStateAndLocalIncomeTaxes xmlns:us- >0.003</> \n<us-gaap:EffectiveIncomeTaxRateReconciliationOtherAdjustments xmlns:us- >-0.004</> \n<us-gaap:EffectiveIncomeTaxRateContinuingOperations xmlns:us- >0.375</> \n<us-gaap:ValuationAllowanceDeferredTaxAssetChangeInAmount xmlns:us- >260000000</> \n<us-gaap:UnrecognizedTaxBenefitsDecreasesResultingFromPriorPeriodTaxPositions xmlns:us- >1000000</> \n<us-gaap:UnrecognizedTaxBenefitsIncreasesResultingFromPriorPeriodTaxPositions xmlns:us- >52000000</> \n<us-gaap:UnrecognizedTaxBenefitsIncreasesResultingFromCurrentPeriodTaxPositions xmlns:us- >18000000</> \n<us-gaap:UnrecognizedTaxBenefitsDecreasesResultingFromSettlementsWithTaxingAuthorities xmlns:us- >14000000</> \n<us-gaap:UnrecognizedTaxBenefitsReductionsResultingFromLapseOfApplicableStatuteOfLimitations xmlns:us- >1000000</> \n<us-gaap:UnrecognizedTaxBenefitsDecreasesResultingFromForeignCurrencyTranslation xmlns:us- >0</> \n<us-gaap:UnrecognizedTaxBenefitsIncomeTaxPenaltiesAndInterestExpense xmlns:us- >84000000</> \n<us-gaap:IncomeLossFromContinuingOperations xmlns:us- >1294000000</> \n<us-gaap:UndistributedContinuingOperationEarningsLossAllocationToParticipatingSecuritiesBasic xmlns:us- >-9000000</> \n<us-gaap:NetIncomeLossFromContinuingOperationsAvailableToCommonShareholdersBasic xmlns:us- >1216000000</> \n<us-gaap:IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity xmlns:us- >0</> \n<us-gaap:NetIncomeLossFromDiscontinuedOperationsAvailableToCommonShareholdersBasic xmlns:us- >0</> \n<us-gaap:NetIncomeLossAvailableToCommonStockholdersDiluted xmlns:us- >1216000000</> \n<us-gaap:IncomeLossFromContinuingOperationsPerBasicShare xmlns:us- >1.64</> \n<us-gaap:DiscontinuedOperationIncomeLossFromDiscontinuedOperationNetOfTaxPerBasicShare xmlns:us- >0</> \n<us-gaap:EarningsPerShareBasic xmlns:us- >1.64</> \n<us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare xmlns:us- >1.64</> \n<us-gaap:DiscontinuedOperationIncomeLossFromDiscontinuedOperationNetOfTaxPerDilutedShare xmlns:us- >0</> \n<us-gaap:EarningsPerShareDiluted xmlns:us- >1.64</> \n<us-gaap:WeightedAverageNumberOfSharesOutstandingBasic xmlns:us- >740500000</> \n<us-gaap:IncrementalCommonSharesAttributableToShareBasedPaymentArrangements xmlns:us- >1800000</> \n<us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding xmlns:us- >742300000</> \n<us-gaap:AntidilutiveSecuritiesExcludedFromComputationOfEarningsPerShareAmount xmlns:us- >14200000</> \n<us-gaap:Depreciation xmlns:us- >2092000000</> \n<us-gaap:InterestCostsCapitalized xmlns:us- >64000000</> \n<us-gaap:EquityMethodInvestmentDividendsOrDistributions xmlns:us- >425000000</> \n<us-gaap:GoodwillForeignCurrencyTranslationGainLoss xmlns:us- >122000000</> \n<us-gaap:RepaymentsOfLongTermDebt xmlns:us- >134000000</> \n<us-gaap:AccrualForEnvironmentalLossContingenciesChargesToExpenseForNewLosses xmlns:us- >285000000</> \n<us-gaap:AccrualForEnvironmentalLossContingenciesForeignCurrencyTranslationGainLoss xmlns:us- >2000000</> \n<us-gaap:EnvironmentalRemediationExpense xmlns:us- >234000000</> \n<us-gaap:EnvironmentalCostsRecognizedCapitalizedInPeriod xmlns:us- >80000000</> \n<us-gaap:AssetRetirementObligationLiabilitiesIncurred xmlns:us- >6000000</> \n<us-gaap:AssetRetirementObligationLiabilitiesSettled xmlns:us- >3000000</> \n<us-gaap:AssetRetirementObligationAccretionExpense xmlns:us- >3000000</> \n<us-gaap:AssetRetirementObligationRevisionOfEstimate xmlns:us- >7000000</> \n<us-gaap:OperatingLeaseCost xmlns:us- >484000000</> \n<us-gaap:FinanceLeaseRightOfUseAssetAmortization xmlns:us- >58000000</> \n<us-gaap:FinanceLeaseInterestExpense xmlns:us- >25000000</> \n<us-gaap:ShortTermLeaseCost xmlns:us- >213000000</> \n<us-gaap:VariableLeaseCost xmlns:us- >199000000</> \n<us-gaap:SubleaseIncome xmlns:us- >5000000</> \n<us-gaap:LeaseCost xmlns:us- >974000000</> \n<us-gaap:OperatingLeasePayments xmlns:us- >482000000</> \n<us-gaap:FinanceLeaseInterestPaymentOnLiability xmlns:us- >25000000</> \n<us-gaap:FinanceLeasePrincipalPayments xmlns:us- >58000000</> \n<us-gaap:RightOfUseAssetObtainedInExchangeForOperatingLeaseLiability xmlns:us- >185000000</> \n<us-gaap:RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability xmlns:us- >178000000</> \n<us-gaap:PaymentsForRepurchaseOfCommonStock xmlns:us- >125000000</> \n<us-gaap:StockIssuedDuringPeriodSharesNewIssues xmlns:us- >4764554</> \n<us-gaap:StockIssuedDuringPeriodSharesTreasuryStockReissued xmlns:us- >0</> \n<us-gaap:DefinedContributionPlanCostRecognized xmlns:us- >156000000</> \n<us-gaap:AllocatedShareBasedCompensationExpense xmlns:us- >171000000</> \n<us-gaap:EmployeeServiceShareBasedCompensationTaxBenefitFromCompensationExpense xmlns:us- >39000000</> \n<us-gaap:ShareBasedCompensationArrangementByShareBasedPaymentAwardFairValueAssumptionsExpectedDividendRate xmlns:us- >0.0580</> \n<us-gaap:ShareBasedCompensationArrangementByShareBasedPaymentAwardFairValueAssumptionsExpectedVolatilityRate xmlns:us- >0.2670</> \n<us-gaap:ShareBasedCompensationArrangementByShareBasedPaymentAwardFairValueAssumptionsRiskFreeInterestRate xmlns:us- >0.0149</> \n<us-gaap:CommonStockDividendsPerShareCashPaid xmlns:us- >0.70</> \n<us-gaap:ProceedsFromSaleOfAvailableForSaleSecuritiesDebt xmlns:us- >837000000</> \n<us-gaap:AvailableForSaleSecuritiesGrossRealizedGains xmlns:us- >94000000</> \n<us-gaap:AvailableForSaleSecuritiesGrossRealizedLosses xmlns:us- >40000000</> \n<us-gaap:EquitySecuritiesFvNiUnrealizedGainLoss xmlns:us- >32000000</> \n<us-gaap:OtherComprehensiveIncomeUnrealizedGainLossOnDerivativesArisingDuringPeriodBeforeTax xmlns:us- >-32000000</> \n<us-gaap:GainLossOnDerivativeInstrumentsNetPretax xmlns:us- >82000000</> \n<us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax xmlns:us- >38542000000</> \n<us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax xmlns:us- >38542000000</> \n<us-gaap:RestructuringSettlementAndImpairmentProvisions xmlns:us- >708000000</> \n<us-gaap:IncomeLossFromEquityMethodInvestments xmlns:us- >-18000000</> \n<us-gaap:DepreciationDepletionAndAmortization xmlns:us- >2874000000</> \n<us-gaap:PaymentsToAcquireProductiveAssets xmlns:us- >1252000000</> \n<us-gaap:IncomeLossFromContinuingOperations xmlns:us- >1294000000</> \n<us-gaap:IncomeTaxExpenseBenefit xmlns:us- >777000000</> \n<us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest xmlns:us- >2071000000</> \n<us-gaap:InterestIncomeOther xmlns:us- >38000000</> \n<us-gaap:InterestExpenseDebt xmlns:us- >827000000</> \n<us-gaap:OtherNonrecurringIncomeExpense xmlns:us- >145000000</> \n<us-gaap:BusinessCombinationIntegrationRelatedCosts xmlns:us- >239000000</> \n<us-gaap:RestructuringCharges xmlns:us- >708000000</> \n<us-gaap:ProductWarrantyAccrualPreexistingIncreaseDecrease xmlns:us- >11000000</> \n<us-gaap:DisposalGroupNotDiscontinuedOperationGainLossOnDisposal xmlns:us- >717000000</> \n<us-gaap:GainLossRelatedToLitigationSettlement xmlns:us- >544000000</> \n<us-gaap:GainsLossesOnExtinguishmentOfDebt xmlns:us- >-149000000</> \n<us-gaap:OtherNonrecurringIncomeExpense xmlns:us- >145000000</> \n<us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax xmlns:us- >38542000000</> \n<us-gaap:CostOfGoodsAndServicesSold xmlns:us- >33346000000</> \n<us-gaap:GrossProfit xmlns:us- >5196000000</> \n<us-gaap:RestructuringSettlementAndImpairmentProvisions xmlns:us- >708000000</> \n<us-gaap:ProfitLoss xmlns:us- >1294000000</> \n<us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic xmlns:us- >1225000000</> \n<us-gaap:IncomeLossFromContinuingOperationsPerBasicShare xmlns:us- >1.64</> \n<us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare xmlns:us- >1.64</> \n<us-gaap:CommonStockDividendsPerShareDeclared xmlns:us- >2.80</>",
                       "(6226000000 / 38542000000) * 100"]]

models = {"Llama 3.1 8B (Finetuned for tagging)": "accounts/d0nnw0n9-c1910b/models/finer",
          "Llama 3.1 8B (Finetuned for extraction)": "accounts/d0nnw0n9-c1910b/models/extraction",
          "Llama 3.1 8B (Base)": "accounts/fireworks/models/llama-v3p1-8b-instruct"}


def inference(inputs: str, model, max_new_token=15, delimiter="\n", if_print_out=False):
    config = os.getenv('FIREWORKS_KEY')

    client = Fireworks(api_key=config)
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_new_token,
        messages=[
            {
                "role": "user",
                "content": inputs
            }
        ],
        stream=False
    )
    answer = (response.choices[0].message.content)
    # print(answer)
    return answer


def process_tagging(sentence):
    numbers = re.findall(r'\b\d+\.?\d*\b', sentence)
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    extracted_numbers = []
    for num_str in numbers:
        if num_str in [str(x) for x in list(range(2000, 2025, 1))]:
            continue

        # Exclude 1 or 2 digit numbers followed by a comma and then a 4 digit number (likely day and year)
        match = re.search(rf"{re.escape(num_str)}\s*,\s*\d{{4}}", sentence)
        if match:
            continue

        # Exclude numbers followed by a month
        match = re.search(rf"{re.escape(num_str)}\s+({'|'.join(months)})", sentence, re.IGNORECASE)
        if match:
            continue

        extracted_numbers.append(num_str)
    print(extracted_numbers)

    result = [[], []]

    for i, model in enumerate(
            ["accounts/fireworks/models/llama-v3p1-8b-instruct", "accounts/d0nnw0n9-c1910b/models/finer"]):
        for x in extracted_numbers:
            prompt = f'''What is the appropriate XBRL US GAAP tag for "{x}" in the given sentence? Output the US GAAP tag only and nothing else. \n "{sentence}"\n'''
            output = inference(prompt, model)
            output = output.split("<|end_of_text|>")[0]
            result[i].append([x, output])

    gt = None
    if sentence in tagging_example:
        gt = tagging_example[sentence]
    return result[0], result[1], gt


def process_extract(model, question, xbrl, gt_answer):
    prompt = f""""You are a knowledgeable XBRL assistant that can answer questions based on XML data. 
             You will be provided with a context extracted from an XBRL file and a question related to it. The example question can help you to learn the format of the answer.
             Your task is to analyze the XBRL context and provide an accurate and very concise answer to the question, DO NOT output xml, code, explanation or create new question.
            \nXBRL file:\n ```xml\n {xbrl} ```\n
            Example question: Can you provide the formula for Operating Profit Margin from Example Corp for the Fiscal Year ending in FY 2022?\nExample answer: (50000000 / 3590000000) * 100\n 
            \nQuestion: {question}
            \nAnswer:"""
    output = inference(prompt, models[model])
    output = output.split("<|end_of_text|>")[0]

    return output, gt_answer


if __name__ == '__main__':
    with open('finer_example.json') as f:
        tagging_example = json.load(f)

    with gr.Blocks() as tagging:
        gr.Markdown("""
## XBRL Tagging 

* **Input:** Provide a sentence containing financial information.
* **Output:** Key entities and their corresponding US GAAP (Generally Accepted Accounting Principles) tags will be generated by the base model and our fine-tuned model.

Feel free to explore the examples below or enter your own sentence.
""")
        gr.Interface(
            fn=process_tagging,
            inputs=[
                gr.Textbox(label="Sentence"),
            ],
            outputs=[gr.Dataframe(label="Llama 3.1 8b (base) output", headers=["Entites", "US GAAP tags"]),
                     gr.Dataframe(label="Llama 3.1 8b (fine-tuned for XBRL tagging) output", headers=["Entites", "US GAAP tags"]),
                     gr.Dataframe(label="Ground Truth Answer", headers=["Entites", "US GAAP tags"])],
            examples=[[x] for x in tagging_example.keys()]
        )

    extraction = gr.Interface(
        fn=process_extract,
        inputs=[
            gr.Dropdown(
                ["Llama 3.1 8B (Finetuned for extraction)", "Llama 3.1 8B (Base)"], label="Model", info=""
            ),
            gr.Textbox(label="Question"),
            gr.Textbox(label="XBRL Raw Text"),
            gr.Textbox(label="Ground Truth Answer", visible=False),
        ],
        outputs=[gr.Text(label="Llama 3.1 8b (Base) Output"), gr.Textbox(label="Ground Truth Answer")],
        examples=extraction_example
    )

    with gr.Blocks() as demo:
        gr.Markdown("# XBRL Enhanced LLM Demo")
        gr.TabbedInterface([tagging, extraction], ["XBRL Tagging", "XBRL Extraction"])

    demo.launch(share=True)
