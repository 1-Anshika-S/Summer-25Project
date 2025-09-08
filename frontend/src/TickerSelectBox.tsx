import React, { useEffect, useState } from "react";
import "./TickerSelectBox.css";

import { tickers } from "./tickers";

type DropDownPropsShare = {
  setTicker: React.Dispatch<React.SetStateAction<string>>;
  selectedTicker: string;
};

const DropDownMenu = ({
  showing,
  ddProps,
  searchTerm,
}: {
  showing: boolean;
  searchTerm: string;
  ddProps: DropDownPropsShare;
}) => {
  if (showing) {
    const tickerRows = [];
    for (const ticker in tickers) {
      const tickerItem = tickers[ticker];

      if (
        !tickerItem.companyName
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) &&
        !ticker.toLowerCase().includes(searchTerm.toLowerCase())
      ) {
        continue;
      }

      tickerRows.push(
        <button
          className="tickerRow"
          onMouseDown={() => {
            ddProps.setTicker(ticker);
          }}
        >
          <img className="tickerIcon" src={tickerItem.icon} alt={ticker} />
          <span>{tickerItem.companyName}</span>
        </button>,
      );
    }
    return <div className="comboBoxDropDownMenu">{tickerRows}</div>;
  } else {
    return null;
  }
};

export const TickerSelectBox = (props: DropDownPropsShare) => {
  let [showing, setShowing] = useState(false);

  useEffect(() => {
    console.log(props.selectedTicker);
  }, [props.selectedTicker]);

  const [searchTerm, setSearchTerm] = useState("");

  return (
    <div className="comboBoxWrap">
      <div className="tickerRow">
        <div className="iconWrap">
          <img
            className="tickerIcon"
            src={tickers[props.selectedTicker].icon}
            alt={props.selectedTicker}
          />
        </div>

        <input
          className="comboBoxButton basicInput"
          onFocus={() => {
            setShowing(true);
          }}
          onBlur={() => {
            setShowing(false);
          }}
          placeholder={tickers[props.selectedTicker].companyName}
          onInput={(e) => {
            setSearchTerm(e.currentTarget.value);
          }}
        />
      </div>

      <DropDownMenu
        searchTerm={searchTerm}
        showing={showing}
        ddProps={props}
      ></DropDownMenu>
    </div>
  );
};
