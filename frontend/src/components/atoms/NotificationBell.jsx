import React, { useEffect } from 'react';
import Badge from '@mui/material/Badge';
import IconButton from '@mui/material/IconButton';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUnreadCount } from '../../store/slices/notificationSlice';

const NotificationBell = ({ onClick }) => {
  const dispatch = useDispatch();
  const unreadCount = useSelector(state => state.notifications.unreadCount);

  useEffect(() => {
    dispatch(fetchUnreadCount());
    // Optionally, set up polling or websocket for real-time updates
  }, [dispatch]);

  return (
    <IconButton color="inherit" onClick={onClick} aria-label="notifications">
      <Badge badgeContent={unreadCount} color="error">
        <NotificationsIcon />
      </Badge>
    </IconButton>
  );
};

export default NotificationBell;
