export const TickerCard = ({
  ticker,
  name,
}: {
  ticker: string;
  name: string;
}) => {
  return (
    <div className="tickerCard">
      {ticker} - {name}
    </div>
  );
};
