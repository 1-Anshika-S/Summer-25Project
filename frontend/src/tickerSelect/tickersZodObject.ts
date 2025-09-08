import { z } from "zod";

export const tickerZodObject = z.array(
  z.object({
    Item: z.object({
      cik_str: z.number(),
      ticker: z.string(),
      title: z.string(),
    }),
  }),
);

export type TickerZodObject = z.infer<typeof tickerZodObject>;
