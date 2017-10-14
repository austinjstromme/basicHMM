# external packages
from numpy import random as nprand
from scipy.misc import logsumexp
from scipy.special import digamma as dg
from scipy.stats import norm
import numpy as np

# internals
import context
import Gaussian_impl as impl
from NormalInverseWishart import NormalInverseWishart
from Distribution import Distribution
from Exponential import Exponential
import utils.LogMatrixUtil as lm

class Gaussian(Exponential):
  """
  Gaussian is a class representing a single variable Gaussian distribution.
  It implementes the Exponential interface.
 
  Attributes:
    mu: mean
    sigma: standard deviation
    prior: pointer to NIW prior.
  """

  def __init__(self, params, prior=None):
    """
    See Exponential.py. Params = [mu, sigma]; prior should be
    a Normal Inverse Wishart.
    """
    if (len(params) != 2): raise ValueError("Gaussian initialization failed."
      + " Malformed arguments to the constructor.")

    self.mu = params[0]
    self.sigma = params[1]

    if prior == None:
      l = [np.zeros(1), np.ones((1,1)), 1., 1.]
      prior = NormalInverseWishart(l)

  def gen_sample(self):
    """
    See Exponential.py.
    """
    return nprand.normal(self.mu, self.sigma)

  def get_natural(self):
    """
    See Exponential.py.
    """
    return np.array([self.mu, -.5])/(self.sigma**2)

  def set_natural(self, w):
    """
    See Exponential.py.
    """
    print(" w = " + str(w) + "  and w.shape = " + str(w.shape))
    if ((len(w.shape) != 1) or w.shape[0] != 2): raise ValueError("Malformed"
      + " arguments to set_natural")

    self.mu = (w[0]/(-2.*w[1]))
    self.sigma = np.pow(w[0]/self.mu, -0.5)

  def gen_log_expected(self):
    """
    Generates the exp (expected log distribution) according to the
    current prior.

    NOTE: The returned distribution may only implement
    distribution.py
    """
    # TODO: follow Bishop - change this to return a general
      # distribution you can just get mass on
    mu, sigma, kappa, nu = self.prior.get_params()

    lambduh = self.prior.lambduh_tilde()

    mass = lambda x : ((lambduh**0.5)*np.exp(-0.5/kappa - 0.5*nu*
      ((x - mu[0])**2)/(sigma[0][0]))*((2*np.pi)**(-0.5)))

    return Distribution(mass)


  def get_expected_local_suff(self, S, j, a, b):
    """
    Returns the vector of expected sufficient statistics from subchain
    [a,b] according to a given states object; assums this dist is the one
    corresponding to the jth hidden state.
    """
    res = impl._GaussianSuffStats.get_stats(S, j, a, b, 1)
    print("res == " + str(res))

    return res

  def get_expected_suff(self, S, j):
    """
    Returns the vector of the expected sufficient statistics from
    a given states object; assumes this dist is the one corresponding to
    the jth hidden state.
    """
    T = len(S.data[0])

    return self.get_expected_local_suff(S, j, 0, T - 1)

  def mass(self, x):
    """
    Computes the probability of an observation x.

    Args:
      x: a single observation

    Returns:
      p(x)
    """
    return norm.pdf(x, self.mu, self.sigma)

  def maximize_likelihood(self, S, j):
    """
    Updates the parameters of this distribution to maximize the likelihood
    of it being the jth hidden state's emitter.
    """
    T = len(S.data[0])

    mu, sigma = impl._GaussianSuffStats.maximize_likelihood_helper(
                S, j, 0, T - 1, 1)

    self.mu = mu[0]

    self.sigma = sigma[0][0]

  def __str__(self):
    """
    String representation of the Gaussian
    """
    return ("mu, sigma = " + str(self.mu) + " " + str(self.sigma))
