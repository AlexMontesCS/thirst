#Can i use python multiprocessing for parallel processing? yes. do i want to do extra work? no. bash to the rescue
python3 updateTotals.py &
python3 main.py &
wait

<<com
on windows? sucks.
use this in powershell

(start py .\updateTotals.py) ; (start py .\main.py)
com