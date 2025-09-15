import styles from "./TickerCard.module.css";

export const TickerCard = ({
  ticker,
  name,
}: {
  ticker: string;
  name: string;
}) => {
  const imageSrc = `https://logo.penylo.dev/${ticker}`;

  return (
    <div className={styles.tickerCard}>
      <div className={styles.tickerCardImage}>
        <img src={imageSrc} alt="" />
      </div>
      <div className="tickerCardText">
        <div className={styles.tickerCardSymbol}>{ticker}</div>
        <div className={styles.tickerCardName}>{name}</div>
      </div>
    </div>
  );
};
