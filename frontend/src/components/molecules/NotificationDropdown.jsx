import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchNotifications, markNotificationAsRead } from '../../store/slices/notificationSlice';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';
import { useNavigate } from 'react-router-dom';

const NotificationDropdown = ({ onClose }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { notifications, loading, error } = useSelector(state => state.notifications);

  useEffect(() => {
    dispatch(fetchNotifications());
  }, [dispatch]);

  const handleNotificationClick = async (notif) => {
    if (!notif.is_read) {
      await dispatch(markNotificationAsRead(notif.id));
    }
    if (notif.link) {
      navigate(notif.link);
      if (onClose) onClose();
    }
  };

  if (loading) return <Box p={2} display="flex" justifyContent="center"><CircularProgress size={24} /></Box>;
  if (error) return <Box p={2}><Typography color="error">{error}</Typography></Box>;
  if (!notifications.length) return <Box p={2}><Typography color="textSecondary">No notifications</Typography></Box>;

  return (
    <List sx={{ width: 350, maxHeight: 400, overflow: 'auto' }}>
      {notifications.map((notif) => (
        <ListItem key={notif.id} disablePadding>
          <ListItemButton
            onClick={() => handleNotificationClick(notif)}
            selected={!notif.is_read}
            sx={{
              bgcolor: !notif.is_read ? 'rgba(25, 118, 210, 0.08)' : 'inherit',
            }}
          >
            <ListItemText
              primary={notif.message}
              secondary={
                <Typography variant="caption" color="textSecondary">
                  {new Date(notif.created_at).toLocaleString()}
                </Typography>
              }
            />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );
};

export default NotificationDropdown;
