import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Divider,
  Alert,
  LinearProgress,
  IconButton,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Event as EventIcon,
  LocationOn as LocationIcon,
  Person as PersonIcon,
  AccessTime as TimeIcon,
  Assignment as AssignmentIcon,
  PeopleAlt as AttendeesIcon,
} from '@mui/icons-material';
import { fetchMeetingDetails, cancelMeeting, clearSelectedMeeting } from '../../store/meetingSlice';

const MeetingDetailPage = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { selectedMeeting: meeting, loading, error } = useSelector((state) => state.meetings);
  const currentUser = useSelector((state) => state.auth.user); // Adjust based on your auth state
  const [isMinutesModalOpen, setIsMinutesModalOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchMeetingDetails(id));
    return () => {
      dispatch(clearSelectedMeeting());
    };
  }, [dispatch, id]);

  const handleBack = () => {
    navigate('/meetings');
  };

  const handleCancel = async () => {
    if (window.confirm('Are you sure you want to cancel this meeting?')) {
      await dispatch(cancelMeeting(id));
    }
  };

  const formatDateTime = (dateTime) => {
    return new Date(dateTime).toLocaleString();
  };

  const formatDuration = (start, end) => {
    const duration = new Date(end) - new Date(start);
    const hours = Math.floor(duration / (1000 * 60 * 60));
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const getMeetingStatus = () => {
    if (meeting.is_cancelled) return { label: 'Cancelled', color: 'error' };
    if (new Date(meeting.end_time) < new Date()) return { label: 'Completed', color: 'default' };
    if (new Date(meeting.start_time) < new Date()) return { label: 'In Progress', color: 'primary' };
    return { label: 'Upcoming', color: 'success' };
  };

  if (loading) return <LinearProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!meeting) return null;

  const isOrganizer = meeting.organizer_id === currentUser?.id;
  const status = getMeetingStatus();

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <IconButton onClick={handleBack}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          Meeting Details
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {/* Main Content */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
              <Box>
                <Typography variant="h5" gutterBottom>
                  {meeting.title}
                </Typography>
                <Typography color="text.secondary" gutterBottom>
                  {meeting.purpose}
                </Typography>
              </Box>
              <Chip
                label={status.label}
                color={status.color}
              />
            </Box>

            <Box display="flex" flexWrap="wrap" gap={2} mb={3}>
              <Box display="flex" alignItems="center" gap={1}>
                <EventIcon color="action" />
                <Typography>
                  {formatDateTime(meeting.start_time)}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <TimeIcon color="action" />
                <Typography>
                  {formatDuration(meeting.start_time, meeting.end_time)}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <LocationIcon color="action" />
                <Typography>{meeting.location}</Typography>
              </Box>
            </Box>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom>
              Agenda
            </Typography>
            <List>
              {meeting.agenda_items.map((item, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <AssignmentIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={item.topic}
                    secondary={
                      <>
                        <Typography variant="body2" color="text.secondary">
                          {item.description}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Duration: {item.duration_minutes} minutes
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>

          {/* Minutes Section */}
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Meeting Minutes
              </Typography>
              {isOrganizer && (
                <Button
                  variant="outlined"
                  onClick={() => setIsMinutesModalOpen(true)}
                >
                  {meeting.minutes ? 'Edit Minutes' : 'Add Minutes'}
                </Button>
              )}
            </Box>
            {meeting.minutes ? (
              <>
                <div dangerouslySetInnerHTML={{ __html: meeting.minutes.text_body }} />
                {meeting.minutes.attachments?.length > 0 && (
                  <Box mt={3}>
                    <Typography variant="subtitle2" gutterBottom>
                      Attachments:
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {meeting.minutes.attachments.map((url, index) => (
                        <Button
                          key={index}
                          variant="outlined"
                          size="small"
                          href={url}
                          target="_blank"
                        >
                          {url.split('/').pop()}
                        </Button>
                      ))}
                    </Box>
                  </Box>
                )}
              </>
            ) : (
              <Typography color="text.secondary">
                No minutes have been recorded for this meeting yet.
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          {/* Sidebar */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Organizer
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mb={3}>
              <PersonIcon color="action" />
              <Typography>{meeting.organizer.full_name}</Typography>
            </Box>

            <Typography variant="h6" gutterBottom>
              Attendees
            </Typography>
            <List>
              {meeting.attendees.map((attendee) => (
                <ListItem key={attendee.id}>
                  <ListItemIcon>
                    <AttendeesIcon />
                  </ListItemIcon>
                  <ListItemText primary={attendee.full_name} />
                </ListItem>
              ))}
            </List>
          </Paper>

          {/* Actions */}
          {isOrganizer && !meeting.is_cancelled && new Date(meeting.start_time) > new Date() && (
            <Box display="flex" flexDirection="column" gap={2}>
              <Button
                variant="contained"
                color="primary"
                fullWidth
              >
                Edit Meeting
              </Button>
              <Button
                variant="outlined"
                color="error"
                fullWidth
                onClick={handleCancel}
              >
                Cancel Meeting
              </Button>
            </Box>
          )}
        </Grid>
      </Grid>

      {/* Meeting Minutes Form */}
      <MeetingMinutesForm
        open={isMinutesModalOpen}
        onClose={() => setIsMinutesModalOpen(false)}
        meeting={meeting}
        existingMinutes={meeting.minutes}
      />
    </Box>
  );
};

export default MeetingDetailPage;
