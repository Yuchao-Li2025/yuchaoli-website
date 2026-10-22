---
title: "Regime Learning and Factor Zoo Dynamics"
category: "Work in Progress"
weight: 3
author: ["Yuchao Li"]
description: "Work in progress by Yuchao Li: learning the states that govern time variation in expected returns from 212 factor portfolios."
summary: "I infer the states that govern time variation in expected returns directly from 212 factor portfolios, using an autoencoder and a hidden Markov model. Factor returns exhibit strong common state dependence, and an allocation conditioned on the learned states raises the out-of-sample Sharpe ratio from 0.82 to 1.18 relative to an equal-weighted benchmark."
---

##### Abstract

What states govern time variation in expected returns? I infer these states directly from 212 factor portfolios, without specifying ex ante which macroeconomic or financial variables define them. An autoencoder extracts the low-dimensional structure from factor returns, and a hidden Markov model identifies persistent states in their dynamics. Factor returns exhibit strong common state dependence: expected returns and the attainable Sharpe ratio vary substantially across the learned states. A regime-conditioned allocation raises the out-of-sample Sharpe ratio from 0.82 to 1.18 and earns 5.6% in annualized excess return relative to an equal-weighted benchmark. The results show that time variation in factor premia is governed by a common, low-dimensional state structure that can be inferred directly from returns.
