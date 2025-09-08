import { TickerZodObject } from "./tickersZodObject";
import "./TickerSelect.css";
import { TickerCard } from "./TickerCard";

export const SelectTickerList = ({
  tickerList,
  setTicker,
}: {
  tickerList: TickerZodObject;
  setTicker: React.Dispatch<
    React.SetStateAction<{
      name: string;
      ticker: string;
    }>
  >;
}) => {
  const tickerHtmlList = tickerList.map((item) => {
    return (
      <button
        onClick={() => {
          setTicker({
            name: item.Item.title,
            ticker: item.Item.ticker,
          });
        }}
      >
        <TickerCard name={item.Item.title} ticker={item.Item.ticker} />
      </button>
    );
  });

  return <div className="tickerList">{tickerHtmlList}</div>;
};
