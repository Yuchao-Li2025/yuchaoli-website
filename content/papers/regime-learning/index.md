---
title: "Regime Learning and Factor Zoo Dynamics"
category: "Work in Progress"
weight: 3
author: ["Yuchao Li"]
description: "Work in progress by Yuchao Li: learning the states that govern time variation in expected returns from 212 anomaly portfolios."
summary: "I infer the states that govern time variation in expected returns directly from 212 anomaly portfolios, using an autoencoder and a hidden Markov model. Anomaly premia exhibit strong common state dependence, and the learned states predict subsequent factor performance."
---

##### Abstract

What states govern time variation in expected returns? I infer these states directly from 212 anomaly portfolios, without specifying ex ante which macroeconomic or financial variables define them. An autoencoder extracts the low-dimensional structure from anomaly returns, and a hidden Markov model identifies persistent states in their dynamics. Anomaly premia exhibit strong common state dependence: expected returns and the attainable Sharpe ratio vary substantially across the learned states. The learned states imply economically meaningful variation in the factor-spanned stochastic discount factor and predict subsequent factor performance.
