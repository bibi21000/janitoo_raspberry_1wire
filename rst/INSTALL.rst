Installation
============

Edit boot config :

.. code-block:: bash

 sudo vim /boot/config.txt

Add the text :

.. code-block:: bash

 dtoverlay=w1-gpio,gpiopin=4

Edit loaded modules :

.. code-block:: bash

 sudo vim /etc/modules

Add the text :

.. code-block:: bash

 w1-therm
 w1-gpio pullup=1
