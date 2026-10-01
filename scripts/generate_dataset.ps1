# Bootstrap the included CSV in environments where Python is not installed.
# The canonical, reproducible generator is src/generate_data.py.
$ErrorActionPreference = 'Stop'
$seed = 42
$rng = [System.Random]::new($seed)
$out = Join-Path $PSScriptRoot '..\data\raw\bank_customers.csv'
New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
function Pick($values, $weights) {
    $x = $script:rng.NextDouble(); $sum = 0.0
    for ($i=0; $i -lt $weights.Count; $i++) { $sum += $weights[$i]; if ($x -lt $sum) { return $values[$i] } }
    return $values[-1]
}
function Normal($mean, $sd) {
    $u1 = [Math]::Max($script:rng.NextDouble(), 1e-12); $u2 = $script:rng.NextDouble()
    return $mean + $sd * [Math]::Sqrt(-2 * [Math]::Log($u1)) * [Math]::Cos(2 * [Math]::PI * $u2)
}
function Clip($value, $low, $high) { return [Math]::Min([double]$high, [Math]::Max([double]$low, [double]$value)) }
$rows = [System.Collections.Generic.List[object]]::new()
for ($i=0; $i -lt 12000; $i++) {
    $age = [int](Clip ([Math]::Round((Normal 42 12))) 18 85)
    $gender = Pick @('Female','Male') @(0.48,0.52)
    $geo = Pick @('France','Germany','Spain') @(0.50,0.25,0.25)
    $tenure = $rng.Next(0,11)
    $credit = [int](Clip ([Math]::Round((Normal 650 85))) 300 850)
    $salary = [Math]::Round((Clip (62000 * [Math]::Exp((Normal 0 0.55))) 12000 250000),2)
    $balance = 0.0; if ($rng.NextDouble() -lt 0.68) { $balance = [Math]::Round([Math]::Min(250000, $rng.NextDouble()*160000),2) }
    $products = [int](Pick @(1,2,3,4) @(0.51,0.43,0.05,0.01))
    $card = [int]($rng.NextDouble() -lt 0.71); $active = [int]($rng.NextDouble() -lt 0.57)
    $digital = [Math]::Round((Clip (Normal (55+18*$active) 17) 0 100),1)
    $tx = [int](Clip ([Math]::Round(7 + .15*$digital + 3*$active + (Normal 0 4))) 0 65)
    $avgTx = [Math]::Round((Clip (105+$balance/6000+(Normal 0 90)) 5 2500),2)
    $branch = [int](Clip ([Math]::Round(2.5-$digital/55+(Normal 0 1.5))) 0 18)
    $complaints = [int](Clip ([Math]::Round(.18+.35*(1-$active)+.15*[int]($digital -lt 25)+(Normal 0 .7))) 0 6)
    $calls = [int](Clip ([Math]::Round(.6+1.1*$complaints+.4*(1-$active)+(Normal 0 1))) 0 12)
    $lastDays = [int](Clip ([Math]::Round(-[Math]::Log([Math]::Max($rng.NextDouble(),1e-9))*26+12*(1-$active)+5*$complaints)) 0 180)
    $loan = 0.0; if ($rng.NextDouble() -lt 0.27) { $loan=[Math]::Round($rng.NextDouble()*90000,2) }
    $spend = if ($card) { [Math]::Round($tx*$avgTx*(0.15+0.5*$rng.NextDouble()),2) } else { 0.0 }
    $savings=[Math]::Round($balance*(0.25+0.5*$rng.NextDouble()),2)
    $investment=[Math]::Round($rng.NextDouble()*([Math]::Max(0,$age-18))*1100,2)
    $account=Pick @('Standard','Premium','Student') @(0.68,0.22,0.10)
    $totalTx=[Math]::Round($tx*$avgTx*12,2)
    $logit=-2.65 + .62*[int]($geo -eq 'Germany') + .42*[int]($age -gt 60) + .55*[int]($products -eq 1) + .95*[int]($products -ge 3) + .82*[int]($active -eq 0) + .24*$complaints + .055*[Math]::Max($lastDays-25,0) - .022*$tx - .018*($digital-50) + .000003*[Math]::Max($balance-80000,0)
    $prob=1/(1+[Math]::Exp(-$logit)); $churn=[int]($rng.NextDouble() -lt $prob)
    $rows.Add([pscustomobject]@{CustomerID=100001+$i;Age=$age;Gender=$gender;Geography=$geo;Tenure=$tenure;CreditScore=$credit;EstimatedSalary=$salary;Balance=$balance;NumOfProducts=$products;HasCrCard=$card;IsActiveMember=$active;MonthlyTransactions=$tx;AverageTransactionValue=$avgTx;DigitalUsageScore=$digital;BranchVisits=$branch;CustomerServiceCalls=$calls;Complaints=$complaints;LoanAmount=$loan;CreditCardSpend=$spend;SavingsBalance=$savings;InvestmentBalance=$investment;LastTransactionDays=$lastDays;TotalTransactionAmount=$totalTx;AccountType=$account;Churn=$churn})
}
$rows | Export-Csv -LiteralPath $out -NoTypeInformation
Write-Output "Saved $($rows.Count) synthetic customers to $out"
Write-Output ('Synthetic churn rate: {0:P1}' -f (($rows | Measure-Object Churn -Average).Average))
