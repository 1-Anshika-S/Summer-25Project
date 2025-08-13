// defines a list of tickers that are "the most popular"
export const tickers: Record<
  string,
  {
    companyName: string;
    icon?: string;
  }
> = {
  AAPL: {
    companyName: "Apple",
    icon: "https://assets.fey.com/logos/AAPL_XNAS.svg",
  },
  NVDA: {
    companyName: "Nvidia",
    icon: "https://assets.fey.com/logos/NVDA_XNAS.svg",
  },
  CMG: {
    companyName: "Chipotle",
    icon: "https://assets.fey.com/logos/CMG_XNYS.svg",
  },
  GOOG: {
    companyName: "Alphabet Class C",
    icon: "https://assets.fey.com/logos/GOOG_XNAS.svg",
  },
  FLYY: {
    companyName: "Spirit Aviation Holdings",
  },
  RBLX: {
    companyName: "Roblox",
    icon: "https://assets.fey.com/logos/RBLX_XNYS.svg",
  },
};
