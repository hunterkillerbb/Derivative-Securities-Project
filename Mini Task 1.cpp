#include <iostream>
#include <cmath>
#include <iomanip>
#include <chrono>
#include <conio.h>
using namespace std;

//Function for normal distribution calculation  
double normalDistribution(double x)
{
	static const double RT2PI = sqrt(4.0*acos(0.0));
	static const double SPLIT = 10. / sqrt(2);
	static const double a[] = { 220.206867912376, 221.213596169931, 112.079291497871, 33.912866078383, 6.37396220353165, 0.700383064443688, 3.52624965998911e-02 };
	static const double b[] = { 440.413735824752, 793.826512519948, 637.333633378831, 296.564248779674, 86.7807322029461, 16.064177579207, 1.75566716318264, 8.83883476483184e-02 };

	const double z = fabs(x);
	double Nz = 0.0;

	// if z outside these limits then value effectively 0 or 1 for machine precision
	if (z <= 37.0)
	{
		// NDash = N'(z) * sqrt{2\pi}
		const double NDash = exp(-z*z / 2.0) / RT2PI;
		if (z<SPLIT)
		{
			const double Pz = (((((a[6] * z + a[5])*z + a[4])*z + a[3])*z + a[2])*z + a[1])*z + a[0];
			const double Qz = ((((((b[7] * z + b[6])*z + b[5])*z + b[4])*z + b[3])*z + b[2])*z + b[1])*z + b[0];
			Nz = RT2PI*NDash*Pz / Qz;
		}
		else
		{
			const double F4z = z + 1.0 / (z + 2.0 / (z + 3.0 / (z + 4.0 / (z + 13.0 / 20.0))));
			Nz = NDash / F4z;
		}
	}
	return x >= 0.0 ? 1 - Nz : Nz;
}

// Return the value of a put option using the black scholes formula
double putOptionPrice(double S, double t, double X, double r, double sigma, double T)
{
	if (fabs(T - t)<1.e-14)  // check if we are at maturity
	{
		if (S<X)return X - S;
		else return 0;
	}
	if ((T - t) <= -1.e-14)return 0.;  // option expired
	if (X<1.e-14*S)return 0.;  // check if strike << asset then worthless
	if (S<1.e-14*X)return X*exp(-r*(T - t)) - S;  // check if asset << strike then exercise with certainty
	if (sigma*sigma*(T - t)<1.e-14)  // check if variance very small then no diffusion
	{
		if (S<X*exp(-r*(T - t)))return X*exp(-r*(T - t)) - S;
		else return 0.;
	}
	// calculate option price
	double d1 = (log(S / X) + (r + sigma*sigma / 2.)*(T - t)) / (sigma*sqrt(T - t));
	double d2 = (log(S / X) + (r - sigma*sigma / 2.)*(T - t)) / (sigma*sqrt(T - t));

	return normalDistribution(-d2)*X*exp(-r*(T - t)) - normalDistribution(-d1)*S;
}

//Return the value of a short call option using the black scholes formula
double  shortcallOptionPrice(double S, double t, double X, double r, double sigma, double T)
{
	if (fabs(T - t)<1.e-14)  // check if we are at maturity
	{
		if (S>X)return X - S;
		else return 0;
	}
	if ((T - t) <= -1.e-14)return 0.;  // option expired
	if (X < 1.e-14*S)return X*exp(-r*(T - t)) - S;// check if strike << asset then exercise with certainty
	if (S<1.e-14*X)return 0.;  // check if asset << strike then worthless
	if (sigma*sigma*(T - t)<1.e-14)  // check if variance very small then no diffusion
	{
		if (S>X*exp(-r*(T - t)))return  X*exp(-r*(T - t)) - S;
		else return 0.;
	}
	// calculate option price
	double d1 = (log(S / X) + (r + sigma*sigma / 2.)*(T - t)) / (sigma*sqrt(T - t));
	double d2 = (log(S / X) + (r - sigma*sigma / 2.)*(T - t)) / (sigma*sqrt(T - t));

	return  normalDistribution(d2)*X*exp(-r*(T - t)) - normalDistribution(d1)*S;
	// a short call option. The payoff is opposite of a long call option.  
}

// Function to return the portfolio value at time t (stock price, time) 
double PortV(double s, double k)
{
	int X1 = 180, X2 = 280;  //two strike prices
	int B = X2 - X1; // the bond price
	double T = 1.5, r = 0.05, sigma = 0.38;  // the maturity time, interest rate and volatility 
	return  putOptionPrice(s, k, X1, r, sigma, T) + shortcallOptionPrice(s, k, X2, r, sigma, T) + B * exp(-r*(T - k));

}

// Main body
int main()
{
	double s = 0., k = 0.; // the stock price and time t
	int X1 = 180, X2 = 280;
	int B = X2 - X1;
	double T = 1.5, r = 0.05, sigma = 0.38;

	cout << "\n\n" << endl;
	cout << "Step1: Show the current(t = 0) value of the portfolio according to the payoff\n " << endl;
	cout << "Press any key to continue. . .\n" << endl;
	_getch();
	// Loop for generate the different scenarios at time t = 0 
	for (s = 0; s <= 560; s += 56)

	{
		if (s <= X1)
		{
			cout << "\n The scenario 1 as stock price is less than X1: " << PortV(s, 0) << endl;
		}

		else if (s <= X2)
		{
			cout << "\n The scenario 2 as stock price is between X1 and X2: " << PortV(s, 0) << endl;
		}
		else
		{
			cout << "\n The scenario 3 as stock price is over X2: " << PortV(s, 0) << endl;
		}
	}

	cout << "\n\n\n" << endl;
	cout << "Step2: Show the value of the portfolio at maturity(t = T) \n" << endl;
	cout << "Press any key to continue. . .\n" << endl;
	_getch();

	// Loop for generating the scenarios at time t = T  
	for (s = 0; s <= 560; s += 56)

	{
		if (s <= X1)
		{
			cout << "\n The scenario 1 as stock price is less than X1: " << PortV(s, T) << endl;
		}

		else if (s <= X2)
		{
			cout << "\n The scenario 2 as stock price is between X1 and X2: " << PortV(s, T) << endl;
		}
		else
		{
			cout << "\n The scenario 3 as stock price is over X2: " << PortV(s, T) << endl;
		}
	}
	cout << "\n\n\n" << endl;

	// Generate a simple and messy table
	cout << "Step3: Create the simple table of results\n" << endl;
	cout << "Press any key to continue. . .\n\n" << endl;
	_getch();

	cout << "The result can be organized in a format that: " << endl;
	cout << "\n" << endl;

	const char separator = ' ';

	cout << left << setw(10) << setfill(separator) << " " << "Stock price" << "   ";
	cout << setfill(separator) << " " << "t = 0" << "      ";
	cout << setfill(separator) << " " << "t = T" << " " << setfill(separator) << endl;
	cout << "-----------------------------------------------------" << endl;

	for (s = 0; s <= 560; s += 56)
	{
		cout << setw(15) << setfill(separator) << "  " << s << "  " << setfill(separator);
		cout << setw(7) << setfill(separator) << "  " << int(PortV(s, 0)) << "  " << setfill(separator)
			<< setw(7) << setfill(separator) << "  " << int(PortV(s, T)) << "  " << setfill(separator) << endl;
	}
	cin.get();
	return 0;
}
