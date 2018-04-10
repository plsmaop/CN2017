# HW2 - -Retransmission + Congest control
* Please refer to [SPEC](https://github.com/plsmaop/CN2017/raw/master/HW2/HW2_2017.pdf)
* Please note that it only works on Python 2.7
* Directory Tree:
  ```
  HW2
  ├── Sender
  │     └── sender.py 
  ├── Agent
  │     └── agent.py 
  └── Receiver
        └── receiver.py
  ```
* Usage:
  * First, under `./Sender`, execute 
    ```
    python2 sender.py
    ```
    then the program will ask you to enter the `IP` and `port` for binding and the `PATH` for the file you want to transfer
  * Second, under `./Agent`, execute
    ```
    python2 agent.py
    ```
    then the program will ask you to enter the `IP` and `port` for `sender` and `receiver` repectivley and `loss rate` for droping the packet randomly
  * Third, under `./Receiver`, execute
    ```
    python2 receiver.py
    ```
    then the program will ask you to enter the `IP` and `port` for binding and the `PATH` for saving the file
* During the tranfering, `receiver` will save the received data under the `PATH` and replace the original filename extension with `.tmp`
* Once the tranfering is finished, `receiver` will restore the filename extension
