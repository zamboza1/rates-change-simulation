# LinkedIn Post Draft

## Headline
**Building a risk engine to understand the yield curve**

## Body
I spent some time recently building a real-time analytics engine for US Treasury Yield Curves.

I wanted to get my hands dirty with the actual data pipeline, so I built **Rates Change Simulation**. It pulls daily rates straight from the Treasury XML feed and calculates risk metrics like DV01 and Duration on the fly.

The coolest part was building the scenario analysis. You can apply shocks like parallel shifts or curve steepeners and watch how the risk profile changes instantly. It gives you a much better feel for market mechanics than reading a textbook.

I also made sure to build it right. It’s got full unit test coverage and handles network failures gracefully because I didn't want it crashing if the feed blinked.

If you want to check out the code or run it yourself, the repo is here.

[https://github.com/zamboza1/rates-change-simulation](https://github.com/zamboza1/rates-change-simulation)

#statistics #python #finance #engineering
