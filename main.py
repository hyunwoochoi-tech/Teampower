import asyncio
import io
import json
import random
import string
import time
from typing import Dict, List, Optional

import qrcode
import qrcode.image.svg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, Response

app = FastAPI(title="Team Power Recreation Server v2")

DEFAULT_FACES = [{'id': 'face_1', 'label': '얼굴 1', 'img': 'data:image/webp;base64,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'}, {'id': 'face_2', 'label': '얼굴 2', 'img': 'data:image/webp;base64,UklGRtwZAABXRUJQVlA4WAoAAAAQAAAAgAAAnwAAQUxQSPEKAAABDAZtG0ly+MPe/45AREyAuy0XbQ89ig7hIDrzg9gzXhgrlXmbCy6ct4ve06Jt7ZAk3e/7C+2xbdu2bdu2bdu2bdu2bU+Z+X/ffciIyIjI6PeImAA71rY5kqyMf+8Fi8Nu5FZYAHvg4MEawNJaY+HhY2q1AK2Zivje14iIPyKzavyImACUVRX1re3tAfUaUoFxaxx33tVXnnXmaRtNNEoACahiVUDn3Ojsh5587tknrjtw6yVHIX3yLd/oZ/Lgx28/tsc8gASpGhVg5uOe/YsZhz67dp+dNt9sh/2POP17khYTnSS7bloaQFCpEFVgoVO+J2kx2YyZ3Tw9xlgjB+9fbxQAVakIBRa7rYOM0TyRJN2imbvVMzGh3mok3zl8sQAgaAWoYIZT/iajeTIbdWZMcbdoZN/Lpy47GpAgTRaAfX8go3k6SfdMnuINxkhy6PWj5wcQpIlEMfUVzmieYw5swN0tkuy8duVRgDZNAJZ8j71TTRYUYOYW0Ls+3t5xNFSaQoCxx3UyUk7YYaqCbgmkQ765PqBNoNCNXyWjb7DDxTLGyOEzRiNoyUQxyTU1mrmDhaPqVe7R+cIigEqZFFj0cXp0Z/0ljrVUihb5zxkzA1oaEUx+3M80ZyLzXJO+IjngHslfjx8NlXKoYsO3nMZEBzK9QkiyICkkC7ca+fwyQCiDADv9RzMmeuIdqFQzJrnHGjuPGAmVwvTNRz73ZztOmWZ9gtV2BmrQ9WefegMpSPHR72qcUrwCFNwjAdgg3f98tkWkEMXkXyHxXqPukSRUFaDFC6FSgGKK20iYcSC3IuPKKfTGUyCSW8AEN3qCBw6qsyw8sDlTeuQpUMkLE1847MHtmePKAuQeLCRG3wuaj+jaD/fT8ErmzleZeBULGf2v+aB5KNb6ke7ulQBuAhm4AyvWeJFIDvrmwz+ynWLCdAGgCumAB1JKBlbRHwKkIcEHX3wkeBSUuUumqiQ3WC+Mv84CbUR09JcEywxMZemc5YxbMTDygVaRBhSn27EKA5vOqQ7TDYfjE4/cEZotYMuOxC22D7mgqF5G4ydjIVkCFv2NscxcS57gMo/RuCtCBsVUb9Bcg+qgVJ0yzSQU99QBtyy8MRKSIpjwMUbOGReWXM5IhiyEc1qx6vxvZmiSqF7EyGRGT7ikkJBxImXnE9Qzhl0RUrBbV2QyoyqCCiDgkml6awmTPuxKCfVM91ZoEqb+ipZJFVAFUHEOkCS9PR49JL33AK4EBSihHsFfpoEm7eQ1JgMo85llIOnp7dHapG04HzbVGQUgPDXtWsYkAGWuAiorhl7qrbV+B1ZWofP3maF1U39MSwBwpQDWgfTe01prvSe9PR57HF5Qw7gPQt1K/9PTVEaduJXZ49H6+GitB7zBuqJEPqkQAOt2Z1CpsdfH9mi9p/e0llDwDtTMB7aAAvj0/w6oMoFSFq31ccer3KNHPhogwBfAmcroSrEI6b339PZoPem9r7iHe4x8sqXua66WLtyFniwytJkTl5Cc4cxToe6b5szBWXprj57een88TjDkkHvGV9rqviVnOJFpa21oj7dtBybcx/nXjFDg2wUnnl/03pP2eDwerfWgzBgFenKEA3SuhwD8fMMVHCBh0R+P1loPC1dC7zV1Nu5EXgcF/rRSsAgMbEDoPUlv7dF6D8qBVkM9ZnxrBAS/ZQAvZUjSk/TWx7CHkN5rqCuoOQcWg+LPUkBlnCUsLQBJT1JBdVCAGpdHwL9M32Ngtp6l9yShRDXTCqrgDFY07iUBXZk4AoqzQIm1ymaSXgJm7kTeD8FgGuMBt0jYO5lka75j/Gpikb40wV1YyG5G1gLJBtyDzl0Q/s5wkuURdpPs7J/y76bHJ/QSHDzRe05kzx1G7oGfXuKxMAuQSW+t50B54U7NL8EPn4LFmKx6brFb43X4+v0S6ovHo7Wea5hvRF6Nz5sr9BYBMsshRTljPBSfkWs8QT3plZ7UnDmytO78cy587B9yjQdy5u3///+29V5wXfGA8cPReO8X5iLPJUPvyezR2sqDTN01fjkx3nzZvmIPKHiot94DtLettZ6JRyduO/+ZHdg7Ax6sqGfSWgdIa61n4jEPOnvmBzajpxwdXOnAQia99wy99wNQOOzsmBeY5S96AXNwWaISIPMtuOqHKQF9lVactc0kYRqYAQsvMz6gorjAYzUwScI4U7jEfTeEgC3phVUPUEkd7mD8cjKIYobf6M1FMrgFgxe9phAIbmAsj1sJyYIF6+sibxUBApbqdS8N9RQySMIi93BujABA8CRjYRwO8wlKYTq50jm4OBRAwJ60JtmW3Rt0zJmgWHyIfpX3wB1UuIAed4EAEEzxHe01nD9nvy+PUBderTo4NTy4fh0ETzFe5nMpA7AR+c2M0IRHK8kyoCRQivx6VQgSHiuCJ3TEMmFdMXauDcXs0dzY9R6OTFfhhPO7lRGQ8oDnw7NWxgHQGYvwmzkQkBxwHO0Eu3onys7Z6bwArUhVTPuT54Abqnc5OLAFt9KQBsXBvI5nmuuESfxmYkgGkQk/MgtQUbaVJ3a96l4JRdaArSrhar2Zm4t4EEIm0bb7aSlF5yXXe7mbs3NuaCYo5viD3ohX8nTGHyaDZINiWzNPUfAsVJLSlW6nfDtBQ6JyLy3JGz4HUHqxtSEo5vnfvc7bcFDdslqLPBUBDSsuppVq1L3xDFOlzr13cWgOsngfnTc95YjqwurEhfEZFTQumOg7WlmcqVacUbDKamq2MUIu4cWmcAc8PLg0vt4mkgMCzmQsjQqg6MI5wCnXPrQOFPns2wwuXDK/xvgERHLaidYU6oK11xr3Q0Cuinm76DcSLM505mU75CVoe4v2LMXB6/bJCwHHlQnwWWo8NjfFgr3kRj5NLEDQ8iKtNJ6iXuSkccfcELCte3me1d1pq+YnmOBbWsXRnYOLQfOC4oLxgPmvMxSyYK97UfBcFp2fjobkBsV5jFZlTnb/+daURYiMe4FV7vxh14VmmVZRpGDas393r6zIS1C8AKfQSocK9zgxtKoUhBZZzd2LYlpguKdxdwQULpjqW8ainCy9sbNzAWhxUKz9H/2qZzV+OQmkBFCs8qfzkiJfai8HWrATX5JH7oeAUqpO9K15Rc5Vy4KAU16SsWMBaEkU8/XSq+jnqSElEbS/TKse59CS0JIg4OAqovE4hLIo5uuhV0/kDdCyQPQ+xjzgudy3QihNwKo18xwEnsjZMQO0NBC9k5aHsn4C48WiKK9ikX56Lk/sjEtrKBEU19Cqhe4bI4QgpQmystGrxfjULAAQpCSKg9xZub8/dfQKAQjlEDzisXKcZHxxpzFQLUPAgbTKoVsk+ebaQCiBYqpf3SqHpJvRr50BoTgoTmCsIpLm/HFDBC1MdMzLjNVERg7sAgQtCIr5/iYvyk67eBpAghSCgA0G4UVp5I9Hz4jCA04wr8o9kn/es/30mTRo0BTREFRbWib8nXlZNCP5awYV1KsAkIDUKX/5ukjSoxGAqEAVWGi/Ww+eA1ANQOuCqyy3yCKLH/W1LzuBpEMUgALLPThAsuuicQDat3ltiKwNG8nLyqjA1DMK5r5tiLQYyecXXfrkN5hq5uvHDDf88e/TN/+mHZX437dKEMDXTWHxT5jYcR7t8fVXfmTNPUa3CL4DsWocL5ec42V85z8VrwGfmncIvC7uYoUaWzyDT0DFLV4Yx6QGvmyuoALen9vUd4QVPuM5SuywtQZfCwXuAfgiAQBWUDggxA4AAJBIAJ0BKoEAoAA+XSSNRSOiIRqqjqg4BcSygGXRLy/+DL1SkLQ8Nwrdum8T/uv6UGDPchcafUOJn4i6oPffBzN3HGugD7S8s95Innvqff5D6QPmB/4vuq97v59/pvYM/l/9h/6vAn/ssxo3z+Ra53MbMNDhzvAOeeSPyUZHpRM+r5mNLfHfz/I/FdXCgwubXL20eiPtEMlDYmrK3rP/0YyRYsMZjr9eyzgzYYp+vn0zKHWZdW78RAcn/Weo+NfmWmTURiiPVSUp1jSfxx9hlbrfifMeM6PIcMxGeTQ5FVwOrqCQ8LPC/N6zUKKT+ACm/R5/zDs6uivDXZCP12BnwQ4a5r2asmeWgpN5T7sd302vAANQcxv8B0sEQssx2e2l0DfvBUzpHf/b70+3R932D+wQI0sQ6VMR50N4kiomHXRHUzXjXQOrXE4qJGDnjs9PG9+3BlaYJlu4WYQQPMJMfO/Z0Z5oP4qajPQH2XXKCTNeLBvHrZauJRxyxfJPyJi4SmAsELLY/E5nxNzFGL5TD3YMMkDMT7m6ytIQW/TPsE9CCuykz6SuJyLb+gJWbKDW4jF/tJEPvL/5tap6IyNLJ5T8bmwH+/xrFtZCznZic/RhxpX9Kk7NV8fINmqkbkp6m+ef23hfVJ2oQqESA06MPQjsBf2TwXIXBMmKmieOVnonC024oKU3VwbbUYj3y+xmsxhRzb9734WfxuJKiVnQQ9sZvPT+T+Krey8HceH3jB1vb29AZl/JWwPggYJ+9Za2FlEwLyKffESeT5frSfAA/v5HisIrAcBfum1sBHpy3+iDbYE//VVNW15vHGWAUWelghO9xr/mG/1NZhpu4JlluPaMahbBaUsVKYUK5jQLeawdGqdLUuTf0/t9M4UyLeu5luJyx9Ycg7C/C5P0wQgLtFxEHcmWES3tuVVOv4YVnd9WSMkCzxLrCSaiiiDwTfabYJtmL5ClFMUDFK8tlRlzXUe1GCG9wh3gAtTV0dEeRaHV4W910Dlon82eHSzBvQz5GFSVWW2M+bYemsdjdGKIKpEei+tErB+9TN68+kxaiIINViIYGzyga5PSdIh/HcdncOFhR/1QWyQMQQiBhBeyVBz5mx3lh9nG8Tevio8cPEWCMbOUY31vViH/bs9TthPL6lyn/+ubHLGpgJorD64M6y5Tbgtv7/8EDKQiOi/WpBRu8UPiEU3MmiShm4Gu9q2NTUDGTsOXw7ONBbKoa18yBnQAA1P/j/YKn/QM6h+aC/hoT6nz3+0OZylLd37X+7/qcfDDImfIHcacmx0jfc62sRfMfMBwGZNbJFB9SmzGwXFmvpoWtCNxRZdEiqbS1cSrqgspTv+Jpw5Y9Rslpss7M9ujroHi24j87F/WOb8XkXcrh12WvG8ztKrwQFd2AbzM6+B+7lgwsvaCpPj7YVum2lKtiZzFf+u1Q04NyL2qNSbyjApMjrk8/JdltIsFFzuTkGh1IGtoTXM8ulPGwthsEnfPgz9AdXVPKE+XajiF10UY0L2kkewFzQL/uht/jp8a3RWp1FefEgnOGuihNNFRvT9Z/BAvC6ZWfJ2Jv8X2YrRklIa2f1+zZhuH+o/vB0bLSj+jEU+IMp1+7av/peuuVdrcsCmDlMH+ygbcs/c/amwpu0AYPtIZ8haxloXyUUkStaAQScwCBTXDXg4Sr77HUiZzwYFmGhBKddhatYKcLTyTvJVy9O9Y+7R8C8fewIbsvOnxmH3+b0ZLoZ5Jo0bAm/ij0jmj0bsfYluVM5BRTIO5tiqZg08jbTrXGN+zBsQ9dRDtCHVJsWmtxwnAgyR77Od99PJ/nFcdGTHDPFEx+o1LfhBtJi3iSInc4kpxsQ3Vh3kTsDbmnP268zxNMoAZczDFESmNXWUP4Bf4vKlaSPh7I1evDh698NCpiF7BbRpdQekLkhEP4uUqiEa6qU2A6Nl2so0D/LMhewX4knRa4RHNexRxENttPzkxm/sb0mQTPh2yBhWqxF3NV/b+m4bjmw7M8rxup9mHDf5nQmRTTEAvrZ3mTqA09xcsicvGCYP4FyBnt1gBTfToXuBmFoMghLE6ZDfWeVXg0ZfEAAIUraPwwKDhUmpTAbYJbwGTeYL9Yv5kETUShC/5YpXLEr0GwSuK0APakUrUKlUcxJ9UVb8EYguSJn5lwcAGX7dY/HhNb9cJWNACaAnF3vksnlZHUhvgAeQ7CK8RrC3cP0zuoXkw79mGC7OG/rl4zO7wnvbrR5qyj/tdWvpEm6ss1oql+qS8aE7jj5mR4DxbL2GbCst/+FbeMZwmnPjLJ+B7haXJVqRYXXBfeSTAV6w5AnvYggVW5cSL4y/VB0j8nFwLWbDmnTmkTSKSaYVGlLff9pyv3OUh6ay2C8R9I4xHlzYQgdEWf7MtMeuFFwh+eHL578IqJBGI3vRSlqcl6PR5YI15RPOPV/T+aJJndxMMgrir3DrHUUAy0zMZt3FdbhQCkQkqCPdRshn0R/IBVdNUeGrZX+J0pxkYSMb2c/sIIqvo4lTrQ57adBr4IjvnGdjGv322WfRZa0Y9xFhLVteyRI8X//clWpmWjGrUcJF7+ZLtVMuD6nxnkAEry9OL7Mxin0kSquyPjH+20n7FtSYeyfdYKbrvPR3eG6Bm5V6bpF+eutCVpvzRXtDjHMAa4vQJyt/9tr1Suuyn0CkU5rqLpw1xMyvd8Yn5QO7Wz+P6HQp6l3YMADfnL4MXXRuGuxazmLX5+jMJiDZN0WoPNVn7R68MkPEOqRXfZb/07Q4OZJj6rWR9r3BWgV1s6gPBjpHaI0ndywQaBW+GLtTo3iFGpp1vK620Tuwov28A/D8O6Yy2bvasgPJalnJkJKTRhCBKsVzRo5wNMb8eM/m4//HZPWf8QyZc3aNmng/vCCTna1+K9Mowngjeuo/d5/N7FXlBY/AP79Tlb/wQYGmFO+FBgNNoilcvF9nmIE/IBNdK2lUpbTVI4evMtgreGtsPWWqHs2ueU/evRSljXN/fFRuM9HM3gutBzd7SD9XMRjopkhL0mkkgLW9CKOLtpYNx75BDcg/jjLKKU5MgGgVN3rCGfcy93pB/mDYrs6z3SyNV8tBpnibQVmkPSFdl76eBBjiB9Gf61seSTAhcnnEIwp9rWHEW+jAS98DDCQ4Aoo/aguS8gUEPOfIyR+P68Bx4CC+VS5pf6lXU9feD2zVS1oudFj5acy+OlnibmShvddJm959YOIErAdii1nzBbycv5ae9qm/x3DALwmjnISMEsEu07kRUOm7T8JHWe9aPNDmmYawDZDNWc4Fz8rCYiJG/oOesSl038kLep8pvaGdp1zTDzKaZzL8B24zHgt0DrGF5q2leAJ37KiUOa2PMMhV9EqWsAHsYgs/JXvVHwe1ge9lp9HOLv6aaZWe2bNWUKW2GeEjoXjZALSqZ3f604rvD0O/mt9+vx35PtCHvFZLYoZwVW1YnY7D1EBaKy4tVfBPBFtDT4lhE57xdJ3f3b+xb3rHuAe0JMGXUbXf6v7kZfla2hcQFaYAH5qD3YxYifh0rn503Ab3lDeSYuAvZgEBqBV4R22RshgJZbyeP9o+4Z7+JmSHZ3VQ30qIc+LwP4SfDwiyul6LwupnJeGUSalKIFuotIEMN8L7EZWhi8R1Kx/J/+Py+wkeZjegjTXAemeUinEEBwuuTqTwt6vd2SVxiZKNRMqJ5AgK+imd3wJ4qBiZUFHLMEClLMFlcLzwS220Ob0bCzp+E7z5Aijl6+86JdksRb1J9W/k0yA5E+kc94n/R0J+uuUjIlK0VT3oZzFWyf/mBkX/zPZECe11Bu+tBTaw4sc55PKOBUbtxnRt+dSiqCQY1y/8wNYPP1Go1go5Ue6jdTpjDC9rhEl4JsFNM/O3svV9Exx+L5zgElH0cvoFth/0FS5XjGKRaiugJPBxLEhRDr/tPKxRXEpJjmyKhvSQrM3dXO4tvVQZIGybEbO7iD+cYDOQ+CSKpo/AOz9HS98017TJC+vWTOPmfwlrO/gwUBsEtQ21l/SXOQByA++bb7wM13hZKxYJW8CWO82PS8ejdo85bnHeTQHBrAoVWAsgVb1URipBgIRS90jiTwlO1ecOaGg7CblqetDTmmb/oAB62OzGzpI63soXwAFoApA9NU2kwausz7j7uU5CDy5M9r9E/M3rtBum6MEH0/zZ2J7/A1dnC1CNwuJU3kqpV/xTCCUKZ7OtvLEG1w1AwPIcUGQTKmSvYS2fUeRf1DQ4Yu45KuP19cfij+dyDq0zlF/VW/kQ6qHdWiSleHG05DVy2Uze79tV9hDerPmXbYD2ra0Bw6SnvWF8JSMJWQbTw5S0HpJ6O9+HL9m6xmcDnm4hfzKkJ14aNTrBHdkSi8pktzbrAm72mBAHp8GOPPIBWBn2ysDTl+D8w+mF7rWhyMJeAr46Ogfw/5JRkQKeHt7yVBhxFsR3QSLAdvWVrqS6vsMlgxzL91t5fdPjebzLwCR1wyRzfqpMOusb4wI3VfUCU+aTn2Vm1P4haOMk55fQbHgkunRHmuSL725WUMNkyQ6dcQo+PRtQ0GuE9fNFfY57i6WRX+tWQcvgXl1muZW7M7ULEcAHBNPc1vDe6mSQ66mhAyAMhZJ7g/sHqXxuGIO/H68yA16YzNB5V5KkZBjyBs7ST+jPlFSAHEVOY16kpkdyeWndwE1uP1Updc8Q6nFr3e6WjPiKvqW3Opway/k/IBJ2vx/qOTR7azY2BbP4+qzrrMop2VV+fCikFFxy7q5KoJDPHuWtRZ2ijLtqNNDTrw00LQOuxJbKdmsldo2Qnd47jUZ1Gj95v6a1ZXvCzrq3r3nTU2WkkDSMeN1b6hQkr4bhBpqz9Y+NlNdHRw7FbysiGSmDRdCsCSd6cmYyLmyf9tiaMbCkJso7o4YdH+Rxb7PGDWS5CmXn08c+8nVdXqE6XOofCYxmMMQD/igdp9wq/166IebukJjfLy4Nk8bpVaBLb/kQKRLhojOy9GI+r/HvZbbNOGrMRZx9/iaZc1tZSQb828A4KCAyLV6mSU4Hp324HCLQd1IAAAA=='}, {'id': 'face_3', 'label': '얼굴 3', 'img': 'data:image/webp;base64,UklGRhAYAABXRUJQVlA4WAoAAAAQAAAAiAAAnwAAQUxQSBwKAAABsIZtmyFJVkRm96xt27Zt27Zt27Zt27Zt21Z3z6mIeK+rMvNTZJ3fEeFQkp0oeoTDcCywmERRP8Blcd6Xpau5SZaaZ5Zljr708ksOW2Op5ZZfYbklFp6k0bWyLLxrufNFLW/YBPPtevwV7/378zd/onJhYGj48KF///7kxjP2WnL6MRpdbDGKsjamcdc/9elP/0bDxcqBdn++c92R607a5vo1zrAlDrz3s/rkh1DVTai5VHcxhEZPvrnrmg2dbyWnGssUK5/zymA1+Z1u2UQ5cC7FTicA+G8B177MsjojNr/uKwAgy2oYiKEzHOu7sm1L0rm+Na/5tjbHtT+cLysuntYt2gXfHcRaT1RDCo11KCtBdYCggO1dv2+XlJjrQYLTIFWC+ksiPpzVsdn55GU1j2Mf8iNYuZBEh5As1ISf9uh3ZW5mQyCX0+/3KtBhVp6wjvCkicDjc7m8jRVV2XFW2f66F77tpiJ/RjKj1CVSxB8Hj9Bl5vQr3v7CRw15KRIPol5AKkkC8Ozi3Saz+ZkuH6wLiZgap59g4TFMsWv84uAxpSsz+XnfQwwxQuCEWSpmajBvmzgLFW6ax1JA02mLUkXkBerMdxfIQb44EwovyGVKSZurMX9c3BX28VI/pKQGJNKqKULl9MMs1uR9/61gxabF6pBODRh6pL/wxgJ02p9lA9IyZF0hVyxqtJFxmX63o2Q84kHKJ0g4YRHvju0No67xN90n3BqQCiiR9GIhomPtomrtLPKmeC0KwYotCsKO/zOrVZVuaokb/qvXMWIoDURZdFO/N/rVqW7voObbmkgpLOxLk9wxX2qYXbkTuuh8V5jEp6CTYOHyRr9O6/Xk/a6dqByyWI6YZiDgDFfqWxjtPiQoSdoRSUoVxYEl1ayimOZj6PovY7LTYaIZI96eQMnyfW537Q9BZhoSKramSBqBmnWRLupKlXneU0FhDErUvwHrv/k1VLi+g36TKhThImUng/Ym0VUKFG7sm8CkNcOSJWGLlH6Z1hVy/yhC0okptkOyKbIDIrZypbTGSHeiA4gRVZMsuLYxOkyPlzIzxBf9lyDoJLeS2AJGh8OXl0Vl91cDYEi8bBeZHgaF73Ze5Of6PSW1NpOcDkmbUEdDS0iiwl2GAHvQYxT+W1kanufvlKAmvdAUMZURfppEQmfVY7n2Uil4tV2gpFUEhxN/kKIKfB3RImHkmlUi4AxBsPwAZOpDcwkjWiSK1aTBk8P4yqsMl/ZdpWC41ZqHEgbm4g+XH5Iq2SQabeLB61wmVyeAI3bwLBb9h4B0ZemQBCeOGQIecawwXeDPLnTEj7ZaBUxLMtLrpITfZmcLz/uHFICM1Rizlat2KlSHbMb80kAuJmscO6gopFtZzb+IiK22iKwjKSV8NQ6XseSgCQTUCgywJvOKw82RTKGktbiMtSNgBFqmGmdIKWI7DjtYxBCM2xDNn5JhZw57KECKUmOqukoGdbII9hKDG0ysHVkCaN64p5EYWo3DAVKBztwNq49EOWYhUlSYaQn/zlsw1XYXWB9yAaCw4FmLQHOVQ0vVGHd1fQw7H1QrWmxEpUQDX3NabsukvqdOLXc9ZMKBBteHiE9mpGm1ILSBSOHdoBBq2eZF6TFHzizo4IlRSD23DG+Q0eYNB8mGtzE4+6RGW5CNLDkogsgSqhDUlazsKQIhvTiCI6KF/5UDDCuEWHcCmDUnQLdcWJ2KJv2Cr5iSbBZjg+QWAFRTIhT5NUP1ZjLjdggKC7VLrCDNVv8zSY6EP8lGzkZQCiMyIdl9yHVfmhhRxGHU4TFKpCQUi6RoJQaqvhznu4Da4W1UsIfuJqZwvkkhL0so5p/uQjN4nLqaWV1vjUmKx2SgaNTGAYH3xiQwj4mNCl6TR61Mle87S24c/DMzcTjRt2agLT71jp4lOvM14Yu7EY3+AcIlQycQ5AJEYmO+dMcbbLcTqiVErqq+Wd4DPLAUhXVC0rXaPDUJn5Laiy9+hKoOazbh3XjfI+kFIPkP6FKqpqSSKOBIoogvrkMQqRZRyq6MUIwLEfFsv/PEoeikZ4dgV9JyoTTn+s/ZiIpu7E8RDcQDlcoOsN1Yh9ByhTtGAnEhs7Fq91xpRJxGZJR+fkaoC7wF7LfDKQTcTOgW70Z8kY7YFONbiVsoK7V0R9OVVan2AGxAZMzdPdT4lN1pbzmfQllC3o/0VIoitCNlYL5W1ajD/SBDqqHdlPDlhM476nDqX4Wqqc0Bn0OLMFnNbrrliNjVldxG72dJSO2BcsOIob2gRf7JEfuwIHdz1fvR3mlGWlVZtwpaE8T0dmW0c9F2UEAi/1pUci9XCra/b0FUXJkKrg7sSexfHL3ai2ejmf8iTDFAoMMZ3xZEfDB9bbuXTz5ERPwg2by2IOJT4XN5ZbXhSyG/F/RS9OTXoq50MhwpRq5/QI+AE12fE+IgeZD3rNAEWM+XUuyExp3gCmzZNpDA/28xJ0Th5v8PSSIp80MRD19I+mSRd6N+gNhTCIu70kmjK7oZUmWWsbQKHTlKtzmRaoMnrtwgR1pGEUzZvPpujcUhDVITS7tS/ljggwhts4VEFamr3BUrKBpFXoLOeCLiJlbSBKO+nJeavQVERCx7CrU9PHH2mkMx5bUx2ALaJx2qQEFnIeVV8Kzk094MXFqHGciH4XJlWKIKNHQeYr4IMH7+O62uxAw/JnsWiNq2CLWdbxUdjQhrUnQQOuifdfZjPiK6b5VRnCmOu3izewmji+bsPrzJI58005XErzPJnohnb0lQlBe6oJtc1ZVOxxrpVoTsAGCAgAu07wh4N/ZjNLUX9Wfg1K/VfMA9fJ2LA6jvltUvuJVlFv8GKWMTdE+VzOEruFL/Zs0c9wIh5tiVk9nImuhAVzo9jbD1O0A0BljUVLwSNzrvDMhNeOSnZvJDNNZGeSUivprIgnw3MfXT3MaNpbAUpYQ20YZFn7dI9LnJ39YSoOeoD0+uv5No8bWE2d7lKph6o+C7FUfpr73dZNDklC/rSDZY68dIBt595en9Tb4lULpZvkkyAqnH7EooLOd/Lp7agPrcnrKIFpS8zLSmGCsx+cMGFr840oOC35OdMMjqUsD/9rUQZIsMpiSBdcpClMFZ0HGibWBKfmb07FhsXgm/UfWwQBNWWaoOOpNovNcRFGPI8dyXGDY086cIaL2z+h7NEr8hth9WtMK3SK2HGS3yHVKPwEay/z+AL4f1rxdS6n3UTKadEFsOIz/ySpsc8Ers/cD7CR4itFpvo3Cno/lNr1YzTHgjvRqZK98exjgfRN5071V231WIgpcZexNu/FsByWuVvdlQseFbSJJ31XtTkI5/CRCSYIelF1WLc1t+1a3UajVn+Q2yaS7+q82tArZf65tr/2eB9jKtP8w28t6/tpesPyvp3LxPtpYyfD9wtPOFJ2lqDUx/ozwHSXgTpNfgCjfSU4hCyo4cyWPFV1d5CVZQOCDODQAAsEQAnQEqiQCgAD5dJI9FI6IhmFo/VDgFxLKAZmRCy1juZ1IPtwJzrvph8lXrUfQA6Tf90fUL/r//uwoXkL+//HLz/9B4i4/EEfv+wD91XPFeaee//nfbN8vej386/2XsG/yv+yelv5xnsf/rov8fe72f4dZ9sY2ddfcLaBNl3avIdWcZDooIP3odvCsOf6RAg+Z0WH7R1tlGLF2X7imGVa0mnPqLa4LUrYoU6rFkzcZaBt5atfMwvOYeF0pzl7zfsUdOdgqxsGiSCnDszntlDFE3tVPJM0hOi5azRuGcOvYs90s1jZGd4TtEpCJfjEoPNggMboVDylVJmZfbY8mciAfUzTToB4ZAGqXdHV+3iE1yA4v4aHXbr03kRiITKdoOYrOwSlaMgz9WJH7vXory4yaOGZJ+rMHBO6NFYTB39C7l39mZ2YfNj3BBWGAT/3C76M1evWvecsGD9psxZRtBTKWcMczASqUmj0Lx/ci5hL96ZWa5eP2/lVmRwkV9V9yy8a5PzA0J88IRoHjgSnr6dESnRhlqSDmS5ixnzTVUJcl1ES/21XJLo4dsgXNYUFLiKGQPkIViq5QHrH2IzhL15sEaPOC1PZ69npPCf9Df/w5bK3wpB6TGjNasD6J5Bg7EmkQ+y4N+X/e/b+zGVLM3eORRWHknwEvXb/1LhUmy0T64CW9KEZYv3kBMGQieihoih4mFkEbm10Qnjcp/nWyKJBMWGqCebK+E5wWho8iAAP7+BtQP/EjGRNPgeEsy/4Nca+f9jF31NeheDpQeLbvGhyR+d/yegz92tQaYkcb1idPxfhzPxjdSsTmQDv61z3G3/Xx8ehOGWpr1OVuU0epbcOptLlTpJTQ5cSdXOS7KCJ0OizUvre3tlY10fl/biliw7bBOkhLm57tOMyIb8/SP2K3K15x4uOJ1yYt7111FVP+XNeuPFhk/4rieWJ3fEpJnAYoD8HyUbCMwEffKRMe+CLJwOJ4U+9RGl6XYzGEMISDYyWn+/T7h/5goI/gYOmVcm2jf+YtWa8RG35PREUt86aXxPTTdIBory/cDbOdr6PIYN6wD2f8ntzflJnIRQVQqniqJJoMG0/QBgZRU9/LScm8AUd69BrSqZRAyRA8cp/MP/Kd2rRDslYVEa9bLNvI09E+UWNrQdKbluVLWznvPhWtJzF+ZhTcZKVav3LveuVq71ED1pDprC87d8peLzthW7nn+UUAddMWyaz/R/7dGqkS4kQyLimw/nFUuRSChHzsz8SkFsBbmHIp0/pq9B32uLOFe8L0UpWF88E/hoIAroiDv4vZevexRPN1iARy5hauNqojWItk+v9seXC2LQ3Y75WjQcYTp+09fVqieamL055JwvY05r82a0bKK2Wa+2URdItBBklhelryGIcyNaVMyEr5iQZI1WxKo45s4l6dfnLDTjldK32ED9meGuAFQ/9s3W9CX+31RaTMtRzGa6+t1734mDeqwwva02bWipJDh5+n+LjL5vujjM4X5cPV5q5RUuXHN17+nZwObqxJ435x9/Pdurvm4UtnsAgm6M+fvLscwujuhsTBGmcF7coc4nHn3g26I2dxB3C/fN2Bhchvp2F9ceJVJcrjJHtrN2xnJXAAhL8bRBTdrzx4RawfqQNSh9lekw3UZmPyP8d5PuMx08sKyd36DaGQSqDJko5znZiV/22xwhBWAOlgRSNnvOEP8KLq0jAy9CKjYGKIfw4pJnFttoL2y2bjJ+3pa/wZPb9RJH7Yv3amLGjn1w1T17LQmVxc2HlOhTlvIt0HE6k1KsV6ldClx85nDrDmZCxy1IY4dVRBqS70z72NAroEALTj2KfeLcC6dkmHxoSGTL7cPa2pNHWFN4K4+VZMYVcuYIMbyVvvOexXcEw61nrhD+CnEg382mpwfTxyO9BKcPRqvIV4HQxcN30iPm7k7BHLlxIKAe3fhY47rfk0DKgWNW1ODxUafftxNFUKbcZwAyLXnmH9cFskS6O1kfRJUkltwRlCYMG47s17I5mzeaO82oPIkbZpG+fx/xZXoqOGmwdlF4jWwcI2dIiyehafw5alSOJnPSmSKBt/KG5bN2KF4JzWPf/bHT2C9ngoT8Sn0oi/ceDBz8c92xudpR1d90jCMGyMfxMnH69nrQUArtkipvUtvck190/gQkzjNwEBE8cIBS7P1ol2z5WrmntreMKcNCXvbopJYHxNsBz9mKVFwlsaeP/4+Yw7HsJGbuAG1S6zL1Xt/2lYvhdBOsK/nPsykhh8Unv1U0Hu/3J0q0Ys77TR9VX5uag/tQBSBUGQzItpMD1ipZ2BP3o3DNqnj/DRH5aAuioqovRPcUoLSe+jUyaLQReke1pRwg4xGXmUC65L7ZwHu0jahP7CgXaQ12UOx7IVAYF1K5hFHs1THnzB0DBCM42jvLtB9Vbdc7ZwVdyXFUzTO54XV9kstX7+aTmdKOCvqVSPD0XphYVsSWbYn1/MoclDre5P9BVwtWNOw039VdZP8wvV+pw3CysmY7z3DNc1a3pBO90i5Fjs5ysipa7Xjj2rrQcwNQFHTdtGxJHuhd1fje4fLOY59n4b05EWTxUl1nzb+3/9LVko5KCesXhS9RCNLej1mDhTbjLwiECURtR4KDJMA+3ukthcOAwAvcLF6BSbtYOXO8UvClPaMvdfl6lm4ecezoQpWgFK6fjI6HUNCRpW266KNWL5V1BHFjm5cJV98Rzm8y2XwUI/08igR0p5016rbhXPxG2149K75SFNA2XEaGz3XVDb6NKgoFxSJgaZppaGcpA+5sK7fNIxU9sdE8Bzy7KncTtDL9iN57EdzcNJ1/sUwVSZx9/Vlu1be+VsBQN4hV4/hYPOK4pkbuRs/fDbroA+51gDQ5SyJs7rvxi4kpHtqwWOmywTUN1qhIbSyUQdk5rgs2ZCRU0/ZYDLrTMasXIzYZg8PrDAX2mMVXmM7Gbr/9Fwkp7c3adupxbfIm9gK6pThQHACpe/jGsfwalGlWUeYCbJLSPypv7gjQenk2RJp342g6BEwXN1h1OQlMjjAlQadZljqS+wiVYbUzNMayDW5O1HwepYps1qF5pi0tpf9u6gpqVdyIjlnsb8PKLu3Fb2wEDICyNaPDCGSXSnke3KIRasNBI0eJNL/5EPiRaQoE+l9eBvwV3Qz3DbkwutFkUaMykg8mCrjT88rRFuRILfcBwKIJPx5rb74t9ptcBYBtRWx5n1LvnR3RJlazRRI0u5LjV0mdLnjrQeBdgPn2Evm3ETYMVxaivaTeBCdCO7RvV1KBhmcuNnFYt35VxtNJ3rfgCCjHqTaj39ci4kR4QeEPmAJclBzxNT8ZBqHK6pYMZPD4X512AkSqi+gCirAHdOQgfbi6IuIXuH5g1Yh0DlODf0Y5vIUXK07JON26GUk24CCZda+Cty5S54fS/3qWp+2fIzEcemnoFB5mpF1MywuVABfGltsoDiIMAFPGyZ4Z6PeNMhRnuMsj6hfwuWJtSMwjADaHQTBovtkNHJDw9xF+/1hD+ASylvv191EK9s7hYmtD0qoT2W02E4WT2qTCr8nWusBw6w7SdWdzv/PBLQZJa8aVmw+SYJXB+F1eujDss/tAnuvcPyC98cvkN4Wk4GoxeT/nQ+Uy5L9t07/AVRPgNSUsYNXPlHPXz3wUM630srE6Ph1m/iqRb2iTdZlztrPo/lsodWKyp3PbAjxvisUoLE9s9D9fNDA0WOwPOZpZYZyaYfaJlDX3fFfy3nEuNyR0mZRbmGxbo7BGYZmh9Xz78UAPgW+Xbx42RXzjMLU7ffto+IGTuC79dqu8meg/5VPSVglvG6gN5StqXr3nLjJxEDdwYgEx1yN6aoxDJyI4obR62wqDaRbudw78Q7xsUS9H4im+a940hP6Xo+lIG2j8ROwOHNZ07J154VGWVll4fjRdBRNavvR9yz1Hkg6PoOZBcUfcJmsto+EtKRbzHz70XfwefQ4RWaZgfm5wgtWKkgGzpdlTnmDVWkt1iULz8ZkLo0PZAFRmOFycoPzEtZbSiYH/7zjtf6VPuEZ3tfKlYiMdb7ZJxauTlusfXcqZi+ZZr4ZilzX7VoBZ13jnuoYMv+hj4MpeqtqBSVU8J0OY+gEqoXtWQT0lVTvFHgLHIPzvODcQCEtu5YPsEr7cWi9ErXT8eEKsZakbgXau/VPvy+DKpIBsnfKKE6GzBiYW9boBkt5lfULfy0xHYHQdTeXdD5UcEaQBFcoxgjUG7zEwjJOe364a4FXQULmVGsHDLKbP+0dqeufuhHAnC3XTtkwwS00csh4/raqp9jDkxxjvjt94p4t2LIafsnYznstv32hip128R65zIFwmvFWZCW98ucdsONeBe0PJYrEt14xaEMJv7/8dLr0cynIA5khCoBbAhTrQrgx9Tf5LvY8aBpuvJN1AtrvZbnmtsjJrlOdqaX+ij7jmBhGcyeBXzX9xgM8XNeVYPirtTadpOeu+mXlyc+xifvkUWGll18cVzl03xVyObqHzdn55OBlrp696bhmz/CcrcJPjVRWcjjrRyLmVd+wBXldJqqAzhzs2QkeA8zMdZpPoOwBCSR9i1epAdamWY0ICizU2FeJ+HDl2SqSdSdRdsBz0/enJ3Pfn7VRhAE5mJ9v49Rlosv+mkZ08PFYaPN533eCfv0r8/P0rcv+XFLlzTJ34081Vh4ByVAURGNnZsHnu6kVDjBesAkjCF0NLrQA'}]

FALLBACK_EMOJIS = ["🦊", "🐻", "🐼", "🐯", "🦁", "🐸", "🐙", "🦄", "🐧", "🐶", "🐱", "🐹", "🐨", "🦖", "🐝", "🐬", "🦊", "🐵", "🐥", "🦉", "🐺", "🦝"]
OUTFITS = ["suit", "vest", "muscle", "dress", "tracksuit", "hero"]
HATS = ["none", "sunglasses", "crown", "hardhat", "ribbon", "halo", "horns"]
ITEMS = ["none", "contract", "coffee", "beer", "mic", "money"]

DEFAULT_QUIZZES = [
    {
        "q": "버섯은 식물이 아니라 곰팡이균(균류)이다.",
        "a": "O",
        "exp": "정답은 O! 버섯은 엽록소가 없어 광합성을 하지 못하는 '균계(곰팡이류)'에 속합니다."
    },
    {
        "q": "북극곰의 피부는 흰색이 아니라 검은색이다.",
        "a": "O",
        "exp": "정답은 O! 털은 투명(빛 반사로 희게 보임)하지만, 열을 잘 흡수하기 위해 피부 자체는 검은색입니다."
    },
    {
        "q": "바나나는 나무가 아니라 '풀(초본식물)'에서 열린다.",
        "a": "O",
        "exp": "정답은 O! 바나나는 줄기에 목질부가 없는 세계에서 가장 큰 여러해살이 풀입니다."
    },
    {
        "q": "낙지는 심장이 1개이지만, 문어는 심장이 3개다.",
        "a": "X",
        "exp": "정답은 X! 문어뿐만 아니라 낙지와 오징어 같은 두족류는 모두 심장이 3개입니다."
    },
    {
        "q": "사람의 지문처럼 고양이의 코 무늬도 개체마다 모두 다르다.",
        "a": "O",
        "exp": "정답은 O! 고양이와 강아지의 코 주름(비문)은 사람 지문처럼 세상에 단 하나뿐입니다."
    },
    {
        "q": "금성은 태양계에서 태양과 가장 가까운 행성이다.",
        "a": "X",
        "exp": "정답은 X! 태양과 가장 가까운 행성은 수성입니다. (단, 가장 뜨거운 행성은 금성!)"
    },
    {
        "q": "딸기의 겉면에 박혀 있는 깨 같은 것이 사실은 딸기의 '진짜 열매'다.",
        "a": "O",
        "exp": "정답은 O! 우리가 먹는 빨간 과육은 꽃받침이 자란 것이고, 겉의 씨처럼 보이는 게 진짜 열매(수과)입니다."
    },
    {
        "q": "오른손잡이는 왼손보다 오른손의 손톱이 더 빨리 자란다.",
        "a": "O",
        "exp": "정답은 O! 자주 사용하는 손일수록 혈액순환과 미세 자극이 활발해 손톱이 미세하게 더 빨리 자랍니다."
    },
    {
        "q": "콜라는 원래 감기약·소화제 같은 약품으로 개발되었다.",
        "a": "O",
        "exp": "정답은 O! 1886년 약사 존 펨버턴이 두통·피로 회복용 강장제로 처음 만들었습니다."
    },
    {
        "q": "남극은 육지이지만, 북극은 얼음 덩어리뿐인 바다다.",
        "a": "O",
        "exp": "정답은 O! 남극은 대륙이지만 북극은 대륙 없이 바다가 얼어 있는 북극해입니다."
    },
]


class Room:
    def __init__(self, code: str):
        self.code = code
        self.host_ws: Optional[WebSocket] = None
        self.players: Dict[str, dict] = {}
        self.player_ws: Dict[str, WebSocket] = {}
        self.lobby_ws: List[WebSocket] = []  # Players browsing avatar picker before finalizing
        self.faces: List[dict] = [dict(f) for f in DEFAULT_FACES]
        self.current_game: str = "lobby"  # lobby, fashion, stop777, bomb, rhythm, quiz, podium
        self.quizzes: List[dict] = [dict(q) for q in DEFAULT_QUIZZES]
        self.game_state: dict = {}
        self.bg_tasks: List[asyncio.Task] = []

    def cancel_tasks(self):
        for t in self.bg_tasks:
            if not t.done():
                t.cancel()
        self.bg_tasks.clear()

    def taken_face_ids(self, exclude_pid: Optional[str] = None) -> Dict[str, str]:
        taken = {}
        for pid, p in self.players.items():
            if pid == exclude_pid:
                continue
            fid = p.get("face_id")
            if fid and not fid.startswith("emoji_"):
                taken[fid] = p["name"]
        return taken

    def get_public_players(self):
        return sorted(
            [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "face_id": p.get("face_id"),
                    "emoji": p.get("emoji", "🙂"),
                    "outfit": p.get("outfit", "suit"),
                    "hat": p.get("hat", "none"),
                    "item": p.get("item", "none"),
                    "score": p["score"],
                    "is_bot": p.get("is_bot", False),
                    "connected": p.get("connected", True),
                }
                for p in self.players.values()
            ],
            key=lambda x: (-x["score"], x["name"]),
        )

    def snapshot(self):
        return {
            "type": "state",
            "room": self.code,
            "current_game": self.current_game,
            "players": self.get_public_players(),
            "faces": [{"id": f["id"], "label": f["label"], "img": f["img"]} for f in self.faces],
            "taken_faces": self.taken_face_ids(),
            "game_state": self.game_state,
            "quizzes": self.quizzes,
        }

    async def broadcast(self, payload: Optional[dict] = None):
        data = payload if payload is not None else self.snapshot()
        text = json.dumps(data, ensure_ascii=False)
        if self.host_ws:
            try:
                await self.host_ws.send_text(text)
            except Exception:
                pass
        dead = []
        for pid, ws in list(self.player_ws.items()):
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(pid)
        for pid in dead:
            self.player_ws.pop(pid, None)
            if pid in self.players:
                self.players[pid]["connected"] = False

        dead_lobby = []
        for ws in list(self.lobby_ws):
            try:
                await ws.send_text(text)
            except Exception:
                dead_lobby.append(ws)
        for ws in dead_lobby:
            if ws in self.lobby_ws:
                self.lobby_ws.remove(ws)


rooms: Dict[str, Room] = {}


def generate_room_code() -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(100):
        code = "".join(random.choices(chars, k=4))
        if code not in rooms:
            return code
    return "".join(random.choices(chars, k=5))


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/health")
async def health():
    return {"status": "ok", "rooms": len(rooms)}


@app.get("/api/qr")
async def get_qr(data: str = Query(..., min_length=1, max_length=500)):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


# ==================== BOT LOOPS ====================
async def run_bot_fashion(room: Room):
    try:
        bot_ids = [pid for pid, p in room.players.items() if p.get("is_bot")]
        all_ids = list(room.players.keys())
        for bid in bot_ids:
            await asyncio.sleep(random.uniform(0.4, 1.5))
            if room.current_game != "fashion" or room.game_state.get("phase") != "voting":
                return
            others = [pid for pid in all_ids if pid != bid]
            if others:
                room.game_state["votes"][bid] = random.choice(others)
                await room.broadcast()
    except asyncio.CancelledError:
        pass


async def run_bot_stop777(room: Room, start_ts: float):
    try:
        bot_ids = [pid for pid, p in room.players.items() if p.get("is_bot")]
        async def single_bot(bid):
            target = max(3.5, random.gauss(7.77, 0.85))
            delay = (start_ts + target) - time.time()
            if delay > 0:
                await asyncio.sleep(delay)
            if room.current_game == "stop777" and room.game_state.get("phase") == "running":
                if bid not in room.game_state["results"]:
                    elapsed = round(target, 2)
                    room.game_state["results"][bid] = {
                        "time": elapsed,
                        "diff": round(abs(elapsed - 7.77), 2),
                    }
                    await room.broadcast()
        await asyncio.gather(*(single_bot(b) for b in bot_ids))
    except asyncio.CancelledError:
        pass


async def run_bomb_loop(room: Room, duration: float):
    try:
        end_ts = time.time() + duration
        room.game_state["end_ts"] = end_ts
        while time.time() < end_ts:
            if room.current_game != "bomb" or room.game_state.get("phase") != "running":
                return
            holder = room.game_state.get("holder")
            if holder and room.players.get(holder, {}).get("is_bot"):
                await asyncio.sleep(random.uniform(0.65, 1.5))
                if time.time() >= end_ts or room.game_state.get("phase") != "running":
                    break
                if room.game_state.get("holder") == holder:
                    others = [pid for pid in room.game_state["order"] if pid != holder]
                    if others:
                        nxt = random.choice(others)
                        room.game_state["holder"] = nxt
                        room.game_state["pass_count"] = room.game_state.get("pass_count", 0) + 1
                        room.game_state["last_pass_ts"] = time.time()
                        await room.broadcast()
            else:
                await asyncio.sleep(0.15)

        if room.current_game == "bomb" and room.game_state.get("phase") == "running":
            loser = room.game_state.get("holder")
            room.game_state["phase"] = "exploded"
            room.game_state["loser"] = loser
            survivors = []
            for pid in room.game_state["order"]:
                if pid != loser and pid in room.players:
                    room.players[pid]["score"] += 50
                    survivors.append(pid)
            room.game_state["survivors"] = survivors
            await room.broadcast()
    except asyncio.CancelledError:
        pass


async def run_rhythm_loop(room: Room, duration: float = 38.0):
    try:
        bot_ids = [pid for pid, p in room.players.items() if p.get("is_bot")]
        start = time.time()
        while time.time() - start < duration:
            if room.current_game != "rhythm" or room.game_state.get("phase") != "running":
                return
            await asyncio.sleep(0.8)
            elapsed = time.time() - start
            for bid in bot_ids:
                skill = room.game_state["bot_skills"].get(bid, 1.0)
                inc = int(random.uniform(60, 140) * skill * (1 + elapsed / 40.0))
                cur = room.game_state["scores"].get(bid, {"score": 0, "combo": 0, "perfect": 0})
                cur["score"] += inc
                cur["combo"] = random.randint(3, 25)
                cur["perfect"] += random.randint(1, 3)
                room.game_state["scores"][bid] = cur
            await room.broadcast()

        if room.current_game == "rhythm" and room.game_state.get("phase") == "running":
            await finish_rhythm(room)
    except asyncio.CancelledError:
        pass


async def finish_rhythm(room: Room):
    room.game_state["phase"] = "finished"
    scores = room.game_state.get("scores", {})
    ranked = sorted(
        [(pid, scores.get(pid, {"score": 0})["score"]) for pid in room.players.keys()],
        key=lambda x: -x[1],
    )
    awards = [120, 90, 70, 50, 40]
    awarded = {}
    for idx, (pid, sc) in enumerate(ranked):
        pts = awards[idx] if idx < len(awards) else 25
        if sc == 0 and idx > 0:
            pts = 10
        room.players[pid]["score"] += pts
        awarded[pid] = pts
    room.game_state["awarded"] = awarded
    room.game_state["ranked"] = ranked
    await room.broadcast()


async def run_bot_quiz(room: Room):
    try:
        bot_ids = [pid for pid, p in room.players.items() if p.get("is_bot")]
        for bid in bot_ids:
            await asyncio.sleep(random.uniform(0.4, 1.3))
            if room.current_game != "quiz" or room.game_state.get("phase") != "open":
                return
            room.game_state["choices"][bid] = random.choice(["O", "X"])
            await room.broadcast()
        await asyncio.sleep(random.uniform(1.4, 2.8))
        if room.current_game == "quiz" and room.game_state.get("phase") == "open" and bot_ids:
            b = random.choice(bot_ids)
            room.game_state["choices"][b] = "X" if room.game_state["choices"].get(b) == "O" else "O"
            await room.broadcast()
    except asyncio.CancelledError:
        pass


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    role = None
    room: Optional[Room] = None
    player_id: Optional[str] = None

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            mtype = msg.get("type")

            if mtype == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
                continue

            # --- HOST CREATE / RECONNECT ---
            if mtype == "host_create":
                req_code = (msg.get("room") or "").strip().upper()
                if req_code and req_code in rooms:
                    room = rooms[req_code]
                else:
                    code = generate_room_code()
                    room = Room(code)
                    rooms[code] = room
                room.host_ws = ws
                role = "host"
                await ws.send_text(json.dumps(room.snapshot(), ensure_ascii=False))
                continue

            # --- PLAYER PREVIEW ROOM (to see real-time available faces before joining) ---
            if mtype == "player_preview":
                code = (msg.get("room") or "").strip().upper()
                if code not in rooms:
                    await ws.send_text(json.dumps({"type": "error", "message": "존재하지 않는 방 코드입니다. 사회자 화면의 코드를 확인해주세요."}, ensure_ascii=False))
                    continue
                room = rooms[code]
                role = "preview"
                if ws not in room.lobby_ws:
                    room.lobby_ws.append(ws)
                await ws.send_text(json.dumps(room.snapshot(), ensure_ascii=False))
                continue

            # --- PLAYER JOIN / UPDATE AVATAR ---
            if mtype == "player_join":
                code = (msg.get("room") or "").strip().upper()
                name = (msg.get("name") or "").strip()[:12]
                face_id = msg.get("face_id")
                emoji = msg.get("emoji") or random.choice(FALLBACK_EMOJIS)
                outfit = msg.get("outfit") if msg.get("outfit") in OUTFITS else "suit"
                hat = msg.get("hat") if msg.get("hat") in HATS else "none"
                item = msg.get("item") if msg.get("item") in ITEMS else "none"
                req_pid = msg.get("player_id")

                if code not in rooms:
                    await ws.send_text(json.dumps({"type": "error", "message": "존재하지 않는 방 코드입니다."}, ensure_ascii=False))
                    continue

                room = rooms[code]

                # Exclusive face check (first-come-first-served!)
                taken = room.taken_face_ids(exclude_pid=req_pid)
                if face_id and not face_id.startswith("emoji_") and face_id in taken:
                    await ws.send_text(json.dumps({
                        "type": "error",
                        "message": f"앗! 그 얼굴은 방금 '{taken[face_id]}'님이 먼저 선택했어요! 다른 얼굴을 골라주세요."
                    }, ensure_ascii=False))
                    await ws.send_text(json.dumps(room.snapshot(), ensure_ascii=False))
                    continue

                role = "player"
                if ws in room.lobby_ws:
                    room.lobby_ws.remove(ws)

                if req_pid and req_pid in room.players:
                    player_id = req_pid
                    p = room.players[player_id]
                    p["connected"] = True
                    if name:
                        p["name"] = name
                    if face_id:
                        p["face_id"] = face_id
                    p["emoji"] = emoji
                    p["outfit"] = outfit
                    p["hat"] = hat
                    p["item"] = item
                else:
                    if not name:
                        await ws.send_text(json.dumps({"type": "error", "message": "닉네임을 입력해주세요!"}, ensure_ascii=False))
                        continue
                    player_id = "p_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
                    room.players[player_id] = {
                        "id": player_id,
                        "name": name,
                        "face_id": face_id or "emoji_fallback",
                        "emoji": emoji,
                        "outfit": outfit,
                        "hat": hat,
                        "item": item,
                        "score": 0,
                        "is_bot": False,
                        "connected": True,
                    }

                room.player_ws[player_id] = ws
                await ws.send_text(json.dumps({"type": "joined", "player_id": player_id, "room": code}, ensure_ascii=False))
                await room.broadcast()
                continue

            if not room:
                continue

            # --- HOST ACTIONS ---
            if role == "host":
                if mtype == "upload_faces":
                    # Host uploads additional face photos (data URLs, kept in server RAM only)
                    new_faces = msg.get("faces", [])
                    replace = msg.get("replace", False)
                    if replace:
                        room.faces = []
                    start_idx = len(room.faces) + 1
                    for i, img_data in enumerate(new_faces[:30]):
                        if isinstance(img_data, str) and img_data.startswith("data:image/"):
                            fid = f"face_u_{int(time.time()*1000)}_{i}"
                            room.faces.append({"id": fid, "label": f"얼굴 {start_idx + i}", "img": img_data})
                    await room.broadcast()

                elif mtype == "add_bot":
                    bot_names = ["김계약", "이조달", "박상생", "최발주", "정단가", "한협상", "윤견적", "서실무", "강입찰", "조검수", "임발주", "오계약"]
                    existing = {p["name"] for p in room.players.values()}
                    avail_names = [n for n in bot_names if n not in existing]
                    bname = avail_names[0] if avail_names else f"봇{len(room.players)+1}"
                    bid = "bot_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=5))

                    # Pick an untaken photo face first so testing shows off the uploaded faces!
                    taken = room.taken_face_ids()
                    avail_faces = [f["id"] for f in room.faces if f["id"] not in taken]
                    chosen_face = avail_faces[0] if avail_faces else "emoji_fallback"

                    room.players[bid] = {
                        "id": bid,
                        "name": bname,
                        "face_id": chosen_face,
                        "emoji": random.choice(FALLBACK_EMOJIS),
                        "outfit": random.choice(OUTFITS),
                        "hat": random.choice([h for h in HATS if h != "none"]),
                        "item": random.choice([it for it in ITEMS if it != "none"]),
                        "score": 0,
                        "is_bot": True,
                        "connected": True,
                    }
                    await room.broadcast()

                elif mtype == "remove_player":
                    pid = msg.get("player_id")
                    if pid in room.players:
                        room.players.pop(pid, None)
                        room.player_ws.pop(pid, None)
                        await room.broadcast()

                elif mtype == "reset_scores":
                    for p in room.players.values():
                        p["score"] = 0
                    await room.broadcast()

                elif mtype == "switch_game":
                    room.cancel_tasks()
                    target = msg.get("game", "lobby")
                    room.current_game = target
                    if target == "fashion":
                        room.game_state = {"phase": "ready", "votes": {}, "results": [], "awarded": {}}
                    elif target == "stop777":
                        room.game_state = {"phase": "ready", "results": {}, "ordered": [], "revealed_count": 0, "awarded": {}}
                    elif target == "bomb":
                        room.game_state = {
                            "phase": "ready",
                            "doc_type": random.choice(["Spot", "BPA"]),
                            "order": list(room.players.keys()),
                            "holder": None,
                            "pass_count": 0,
                            "loser": None,
                            "survivors": [],
                        }
                    elif target == "rhythm":
                        room.game_state = {"phase": "ready", "scores": {}, "duration": 38, "awarded": {}, "ranked": []}
                    elif target == "quiz":
                        room.game_state = {"phase": "ready", "index": 0, "choices": {}, "winners": []}
                    else:
                        room.game_state = {}
                    await room.broadcast()

                # --- GAME 1: FASHION CONTEST ---
                elif mtype == "fashion_start":
                    room.cancel_tasks()
                    room.game_state = {"phase": "voting", "votes": {}, "results": [], "awarded": {}}
                    await room.broadcast()
                    t = asyncio.create_task(run_bot_fashion(room))
                    room.bg_tasks.append(t)

                elif mtype == "fashion_finish":
                    room.cancel_tasks()
                    votes = room.game_state.get("votes", {})
                    counts = {pid: 0 for pid in room.players.keys()}
                    for voter, target_pid in votes.items():
                        if target_pid in counts:
                            counts[target_pid] += 1
                    ranked = sorted(
                        [{"id": pid, "votes": cnt} for pid, cnt in counts.items()],
                        key=lambda x: (-x["votes"], x["id"]),
                    )
                    awards = [120, 90, 70, 50, 35]
                    awarded = {}
                    for idx, item in enumerate(ranked):
                        pts = awards[idx] if idx < len(awards) else 15
                        if item["votes"] == 0 and idx >= 3:
                            pts = 10
                        room.players[item["id"]]["score"] += pts
                        item["rank"] = idx + 1
                        item["pts"] = pts
                        awarded[item["id"]] = pts
                    room.game_state["phase"] = "revealed"
                    room.game_state["results"] = ranked
                    room.game_state["awarded"] = awarded
                    await room.broadcast()

                # --- GAME 2: 7.77s ---
                elif mtype == "stop777_start":
                    room.cancel_tasks()
                    start_ts = time.time() + 3.0
                    room.game_state = {
                        "phase": "running",
                        "start_ts": start_ts,
                        "server_now": time.time(),
                        "results": {},
                        "ordered": [],
                        "revealed_count": 0,
                        "awarded": {},
                    }
                    await room.broadcast()
                    t = asyncio.create_task(run_bot_stop777(room, start_ts))
                    room.bg_tasks.append(t)

                elif mtype == "stop777_finish":
                    room.cancel_tasks()
                    results = room.game_state.get("results", {})
                    ordered = []
                    for pid in room.players.keys():
                        if pid in results:
                            ordered.append({
                                "id": pid,
                                "time": results[pid]["time"],
                                "diff": results[pid]["diff"],
                                "dnf": False,
                            })
                        else:
                            ordered.append({
                                "id": pid,
                                "time": None,
                                "diff": 99.99,
                                "dnf": True,
                            })
                    ordered.sort(key=lambda x: (-x["diff"], x["id"]))
                    best_first = list(reversed(ordered))
                    awards = [120, 90, 70, 50, 35]
                    awarded = {}
                    for idx, item in enumerate(best_first):
                        pts = 0 if item["dnf"] else (awards[idx] if idx < len(awards) else 20)
                        room.players[item["id"]]["score"] += pts
                        awarded[item["id"]] = pts
                        item["rank"] = idx + 1
                        item["pts"] = pts

                    room.game_state["phase"] = "reveal"
                    room.game_state["ordered"] = ordered
                    room.game_state["revealed_count"] = 0
                    room.game_state["awarded"] = awarded
                    await room.broadcast()

                elif mtype == "stop777_reveal_next":
                    if room.game_state.get("phase") == "reveal":
                        total = len(room.game_state.get("ordered", []))
                        cur = room.game_state.get("revealed_count", 0)
                        if cur < total:
                            room.game_state["revealed_count"] = cur + 1
                            await room.broadcast()

                elif mtype == "stop777_reveal_top5":
                    if room.game_state.get("phase") == "reveal":
                        total = len(room.game_state.get("ordered", []))
                        room.game_state["revealed_count"] = max(0, total - 5)
                        await room.broadcast()

                elif mtype == "stop777_reveal_all":
                    if room.game_state.get("phase") == "reveal":
                        room.game_state["revealed_count"] = len(room.game_state.get("ordered", []))
                        await room.broadcast()

                # --- GAME 3: BOMB ---
                elif mtype == "bomb_start":
                    room.cancel_tasks()
                    pids = list(room.players.keys())
                    if len(pids) < 2:
                        await ws.send_text(json.dumps({"type": "toast", "message": "최소 2명 이상 참여해야 시작할 수 있습니다!"}, ensure_ascii=False))
                        continue
                    random.shuffle(pids)
                    doc_type = msg.get("doc_type") or random.choice(["Spot", "BPA"])
                    duration = random.uniform(13.0, 24.0)
                    room.game_state = {
                        "phase": "running",
                        "doc_type": doc_type,
                        "order": pids,
                        "holder": random.choice(pids),
                        "pass_count": 0,
                        "start_ts": time.time(),
                        "last_pass_ts": time.time(),
                        "loser": None,
                        "survivors": [],
                    }
                    await room.broadcast()
                    t = asyncio.create_task(run_bomb_loop(room, duration))
                    room.bg_tasks.append(t)

                # --- GAME 4: RHYTHM ---
                elif mtype == "rhythm_start":
                    room.cancel_tasks()
                    start_ts = time.time() + 3.0
                    bot_skills = {
                        pid: random.uniform(0.75, 1.35)
                        for pid, p in room.players.items()
                        if p.get("is_bot")
                    }
                    room.game_state = {
                        "phase": "running",
                        "start_ts": start_ts,
                        "server_now": time.time(),
                        "duration": 38,
                        "scores": {pid: {"score": 0, "combo": 0, "perfect": 0} for pid in room.players.keys()},
                        "bot_skills": bot_skills,
                        "awarded": {},
                        "ranked": [],
                    }
                    await room.broadcast()
                    t = asyncio.create_task(run_rhythm_loop(room, 41.0))
                    room.bg_tasks.append(t)

                elif mtype == "rhythm_stop":
                    room.cancel_tasks()
                    if room.game_state.get("phase") == "running":
                        await finish_rhythm(room)

                # --- GAME 5: QUIZ ---
                elif mtype == "quiz_open":
                    room.cancel_tasks()
                    idx = msg.get("index", room.game_state.get("index", 0))
                    if idx < 0 or idx >= len(room.quizzes):
                        idx = 0
                    room.game_state = {"phase": "open", "index": idx, "choices": {}, "winners": []}
                    await room.broadcast()
                    t = asyncio.create_task(run_bot_quiz(room))
                    room.bg_tasks.append(t)

                elif mtype == "quiz_lock":
                    room.cancel_tasks()
                    if room.game_state.get("phase") == "open":
                        room.game_state["phase"] = "locked"
                        await room.broadcast()

                elif mtype == "quiz_reveal":
                    room.cancel_tasks()
                    if room.game_state.get("phase") in ("open", "locked"):
                        idx = room.game_state.get("index", 0)
                        ans = room.quizzes[idx]["a"]
                        winners = []
                        for pid, ch in room.game_state.get("choices", {}).items():
                            if ch == ans and pid in room.players:
                                room.players[pid]["score"] += 50
                                winners.append(pid)
                        room.game_state["phase"] = "revealed"
                        room.game_state["winners"] = winners
                        await room.broadcast()

                elif mtype == "quiz_add":
                    q_text = (msg.get("q") or "").strip()
                    a_val = msg.get("a", "O")
                    exp = (msg.get("exp") or f"정답은 {a_val} 입니다!").strip()
                    if q_text and a_val in ("O", "X"):
                        room.quizzes.append({"q": q_text, "a": a_val, "exp": exp})
                        await room.broadcast()

            # --- PLAYER ACTIONS ---
            elif role == "player" and player_id:
                if mtype == "fashion_vote":
                    if room.current_game == "fashion" and room.game_state.get("phase") == "voting":
                        target_pid = msg.get("target_id")
                        if target_pid in room.players:
                            if target_pid == player_id and len(room.players) > 1:
                                await ws.send_text(json.dumps({"type": "toast", "message": "본인 캐릭터에는 투표할 수 없어요! 다른 사람을 골라주세요."}, ensure_ascii=False))
                                continue
                            room.game_state["votes"][player_id] = target_pid
                            await room.broadcast()

                elif mtype == "stop777_press":
                    if room.current_game == "stop777" and room.game_state.get("phase") == "running":
                        if player_id not in room.game_state["results"]:
                            elapsed = msg.get("elapsed")
                            if elapsed is None:
                                elapsed = max(0.0, time.time() - room.game_state["start_ts"])
                            elapsed = round(float(elapsed), 2)
                            room.game_state["results"][player_id] = {
                                "time": elapsed,
                                "diff": round(abs(elapsed - 7.77), 2),
                            }
                            await room.broadcast()

                elif mtype == "bomb_pass":
                    if room.current_game == "bomb" and room.game_state.get("phase") == "running":
                        if room.game_state.get("holder") == player_id:
                            now = time.time()
                            if now - room.game_state.get("last_pass_ts", 0) < 0.22:
                                continue
                            order = room.game_state.get("order", [])
                            others = [pid for pid in order if pid != player_id]
                            if not others:
                                continue
                            nxt = random.choice(others)
                            room.game_state["holder"] = nxt
                            room.game_state["pass_count"] = room.game_state.get("pass_count", 0) + 1
                            room.game_state["last_pass_ts"] = now
                            await room.broadcast()

                elif mtype == "rhythm_score":
                    if room.current_game == "rhythm" and room.game_state.get("phase") == "running":
                        room.game_state["scores"][player_id] = {
                            "score": int(msg.get("score", 0)),
                            "combo": int(msg.get("combo", 0)),
                            "perfect": int(msg.get("perfect", 0)),
                        }
                        await room.broadcast()

                elif mtype == "quiz_choose":
                    if room.current_game == "quiz" and room.game_state.get("phase") == "open":
                        ch = msg.get("choice")
                        if ch in ("O", "X"):
                            room.game_state["choices"][player_id] = ch
                            await room.broadcast()

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if room:
            if ws in room.lobby_ws:
                room.lobby_ws.remove(ws)
            if role == "host" and room.host_ws == ws:
                room.host_ws = None
            elif role == "player" and player_id:
                if room.player_ws.get(player_id) == ws:
                    room.player_ws.pop(player_id, None)
                if player_id in room.players:
                    room.players[player_id]["connected"] = False
                try:
                    await room.broadcast()
                except Exception:
                    pass
