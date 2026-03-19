import React, { type FC } from "react";

import * as styles from "./post-footer.module.scss";

interface PostFooterProps {
  date: string;
  timeToRead: number;
}

const PostFooter: FC<PostFooterProps> = ({ date, timeToRead }) => (
  <div className={styles.postFooter}>
    <p className={styles.date}>
      Published{" "}
      {new Date(date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })}
      {/* Reading time hidden for now — uncomment to re-enable: &middot; {timeToRead} min read */}
    </p>
  </div>
);

export { PostFooter };
