export const TopBar = ({
  activeTicker,
}: {
  activeTicker: {
    name: string;
    ticker: string;
  };
}) => {
  return <div className="topBar">{activeTicker.name}</div>;
};
